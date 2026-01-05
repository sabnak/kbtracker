from abc import ABC, abstractmethod

from src.domain.game.entities.ProfileEntity import ProfileEntity


class IProfileService(ABC):

	@abstractmethod
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
			Hash (MD5)
		:param full_name:
			Hero's full name from save file
		:param save_dir:
			Save directory name (timestamp)
		:return:
			Created profile
		"""
		pass

	@abstractmethod
	def list_profiles(self) -> list[ProfileEntity]:
		"""
		List all profiles

		:return:
			List of all profiles
		"""
		pass

	@abstractmethod
	def get_profile(self, profile_id: int) -> ProfileEntity | None:
		"""
		Get profile by ID

		:param profile_id:
			Profile ID
		:return:
			Profile or None if not found
		"""
		pass

	@abstractmethod
	def delete_profile(self, profile_id: int) -> None:
		"""
		Delete profile

		:param profile_id:
			Profile ID
		:return:
		"""
		pass

	@abstractmethod
	def clear_profile(self, profile_id: int) -> None:
		"""
		Clear all shop inventory data for a profile

		:param profile_id:
			Profile ID
		:return:
		:raises EntityNotFoundException:
			If profile not found
		"""
		pass

	@abstractmethod
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
		pass
