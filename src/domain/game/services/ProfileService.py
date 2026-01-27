from datetime import datetime
from pathlib import Path

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.app.entities.Game import Game
from src.domain.exceptions import EntityNotFoundException
from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.interfaces.IProfileGameDataSyncerService import IProfileGameDataSyncerService
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.interfaces.IHeroInventoryRepository import IHeroInventoryRepository


class ProfileService(IProfileService):

	def __init__(
		self,
		profile_repository: IProfileRepository = Provide[Container.profile_repository],
		data_syncer: IProfileGameDataSyncerService = Provide[Container.profile_data_syncer_service],
		save_file_service: ISaveFileService = Provide[Container.save_file_service],
		config: Config = Provide[Container.config],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository],
		hero_inventory_repository: IHeroInventoryRepository = Provide[Container.hero_inventory_repository]
	):
		self._profile_repository = profile_repository
		self._data_syncer = data_syncer
		self._save_file_service = save_file_service
		self._config = config
		self._shop_inventory_repository = shop_inventory_repository
		self._hero_inventory_repository = hero_inventory_repository

	def create_profile(
		self,
		name: str,
		game: 'Game',
		hash: str | None = None,
		full_name: str | None = None,
		save_dir: str | None = None
	) -> ProfileEntity:
		"""
		Create new game profile

		:param name:
			Profile name
		:param game:
			Game entity this profile belongs to
		:param hash:
			Hash (computed if full_name provided)
		:param full_name:
			Hero's full name from save file
		:param save_dir:
			Save directory name (timestamp)
		:return:
			Created profile
		"""
		# Compute hash from full_name if not provided
		if full_name and not hash:
			hash = self._save_file_service.compute_hash(full_name)

		profile = ProfileEntity(
			id=0,
			name=name,
			hash=hash,
			full_name=full_name,
			save_dir=save_dir,
			created_at=datetime.now(),
			is_auto_scan_enabled=True,
			game=game
		)
		return self._profile_repository.create(profile)

	def list_profiles(self) -> list[ProfileEntity]:
		"""
		List all profiles

		:return:
			List of all profiles
		"""
		return self._profile_repository.list_all()

	def get_profile(self, profile_id: int) -> ProfileEntity | None:
		"""
		Get profile by ID

		:param profile_id:
			Profile ID
		:return:
			Profile or None if not found
		"""
		return self._profile_repository.get_by_id(profile_id)

	def delete_profile(self, profile_id: int) -> None:
		"""
		Delete profile

		:param profile_id:
			Profile ID
		:return:
		"""
		self._profile_repository.delete(profile_id)

	def clear_profile(self, profile_id: int) -> None:
		"""
		Clear all shop inventory and hero inventory data for a profile

		:param profile_id:
			Profile ID
		:return:
		:raises EntityNotFoundException:
			If profile not found
		"""
		profile = self._profile_repository.get_by_id(profile_id)
		if not profile:
			raise EntityNotFoundException("Profile", profile_id)

		self._shop_inventory_repository.delete_by_profile(profile_id)
		self._hero_inventory_repository.delete_by_profile(profile_id)

	def scan_most_recent_save(self, profile_id: int) -> ProfileSyncResult:
		"""
		Scan most recent save file and sync shop inventories

		:param profile_id:
			Profile ID to scan for
		:return:
			ProfileSyncResult with counts and corrupted data
		:raises EntityNotFoundException:
			If profile not found
		:raises FileNotFoundError:
			If no matching save file found
		"""
		profile = self._profile_repository.get_by_id(profile_id)
		if not profile:
			raise EntityNotFoundException("Profile", profile_id)

		save_path = self._save_file_service.find_profile_most_recent_save(profile)
		return self.scan_save(profile, save_path)

	def scan_save(self, profile: ProfileEntity, save_path: Path) -> ProfileSyncResult:
		self.clear_profile(profile.id)

		save_data = self._save_file_service.scan_save_data(save_path)
		result = self._data_syncer.sync(save_data, profile.id)

		save_timestamp = int(save_path.stat().st_mtime)

		profile.last_scan_time = datetime.now()
		profile.last_save_timestamp = save_timestamp
		profile.last_corrupted_data = result.shops.missed_data
		self._profile_repository.update(profile)

		return result
