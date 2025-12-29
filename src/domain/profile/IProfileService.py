from abc import ABC, abstractmethod

from src.domain.profile.entities.ProfileEntity import ProfileEntity


class IProfileService(ABC):

	@abstractmethod
	def create_profile(self, name: str, game_id: int) -> ProfileEntity:
		"""
		Create new game profile

		:param name:
			Profile name
		:param game_id:
			Game ID to associate with profile
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
