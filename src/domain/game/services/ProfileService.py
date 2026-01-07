from datetime import datetime

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.exceptions import EntityNotFoundException
from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.interfaces.IProfileGameDataSyncerService import IProfileGameDataSyncerService
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository


class ProfileService(IProfileService):

	def __init__(
		self,
		profile_repository: IProfileRepository = Provide[Container.profile_repository],
		data_syncer: IProfileGameDataSyncerService = Provide[Container.profile_data_syncer_service],
		save_file_service: ISaveFileService = Provide[Container.save_file_service],
		config: Config = Provide[Container.config],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository]
	):
		self._profile_repository = profile_repository
		self._data_syncer = data_syncer
		self._save_file_service = save_file_service
		self._config = config
		self._shop_inventory_repository = shop_inventory_repository

	def create_profile(
		self,
		name: str,
		hash: str | None = None,
		full_name: str | None = None,
		save_dir: str | None = None
	) -> ProfileEntity:
		"""
		Create new game profile

		:param name:
			Profile name
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
			is_auto_scan_enabled=True
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
		Clear all shop inventory data for a profile

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

		self.clear_profile(profile_id)

		save_path = self._save_file_service.find_profile_most_recent_save(profile)
		shop_data = self._save_file_service.scan_shop_inventory(save_path)
		result = self._data_syncer.sync(shop_data, profile_id)

		profile.last_scan_time = datetime.now()
		profile.last_corrupted_data = result.corrupted_data
		self._profile_repository.update(profile)

		return result
