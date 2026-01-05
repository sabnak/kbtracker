import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.exceptions import EntityNotFoundException
from src.domain.game.IProfileRepository import IProfileRepository
from src.domain.game.IProfileService import IProfileService
from src.domain.game.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.utils.parsers.save_data.IHeroSaveParser import IHeroSaveParser
from src.utils.parsers.save_data.IShopInventoryParser import IShopInventoryParser


class ProfileService(IProfileService):

	def __init__(
		self,
		profile_repository: IProfileRepository = Provide[Container.profile_repository],
		shop_parser: IShopInventoryParser = Provide[Container.shop_inventory_parser],
		hero_parser: IHeroSaveParser = Provide[Container.hero_save_parser],
		data_syncer: Any = Provide[Container.profile_data_syncer_service],
		config: Config = Provide[Container.config],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository]
	):
		self._profile_repository = profile_repository
		self._shop_parser = shop_parser
		self._hero_parser = hero_parser
		self._data_syncer = data_syncer
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
			hash = self._compute_hash(full_name)

		profile = ProfileEntity(
			id=0,
			name=name,
			hash=hash,
			full_name=full_name,
			save_dir=save_dir,
			created_at=datetime.now()
		)
		return self._profile_repository.create(profile)

	def _compute_hash(self, full_name: str) -> str:
		"""
		Compute hash from hero full name

		:param full_name:
			Hero's full name
		:return:
			Hash as MD5 hex string
		"""
		return hashlib.md5(full_name.encode('utf-8')).hexdigest()

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

	def scan_most_recent_save(self, profile_id: int) -> dict[str, int]:
		"""
		Scan most recent save file and sync shop inventories

		:param profile_id:
			Profile ID to scan for
		:return:
			Counts dict {items: int, spells: int, units: int, garrison: int}
		:raises EntityNotFoundException:
			If profile, shop, item, spell, or unit not found
		:raises FileNotFoundError:
			If no matching save file found
		"""
		profile = self._profile_repository.get_by_id(profile_id)
		if not profile:
			raise EntityNotFoundException("Profile", profile_id)

		matching_save = self._find_matching_save(profile)
		shop_data = self._shop_parser.parse(matching_save)
		counts = self._data_syncer.sync(shop_data, profile_id)

		return counts

	def _find_matching_save(self, profile: ProfileEntity) -> Path:
		"""
		Find most recent save file matching profile hash

		:param profile:
			Profile entity
		:return:
			Path to matching save file
		:raises FileNotFoundError:
			If no matching save found
		"""
		game_dir = profile.save_dir.split('/')[0]
		save_path = Path(self._config.game_save_path) / game_dir

		lif_files = list(save_path.glob("*/data"))
		lif_files = sorted(lif_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]

		for lif_file in lif_files:
			try:
				hero_data = self._hero_parser.parse(lif_file)
				full_name = f"{hero_data['first_name']} {hero_data['second_name']}"
				computed_hash = self._compute_hash(full_name)

				if computed_hash == profile.hash:
					return lif_file
			except Exception:
				continue

		raise FileNotFoundError(f"No matching save found for profile {profile.id}")

