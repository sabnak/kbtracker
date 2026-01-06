from abc import ABC, abstractmethod

from src.domain.game.entities.ProfileEntity import ProfileEntity


class IProfileRepository(ABC):

	@abstractmethod
	def create(self, profile: ProfileEntity) -> ProfileEntity:
		"""
		Create new profile

		:param profile:
			Profile to create
		:return:
			Created profile with ID
		"""
		pass

	@abstractmethod
	def update(self, profile: ProfileEntity) -> ProfileEntity:
		"""
		Update existing profile

		:param profile:
			Profile to update
		:return:
			Updated profile
		"""
		pass

	@abstractmethod
	def get_by_id(self, profile_id: int) -> ProfileEntity | None:
		"""
		Get profile by ID

		:param profile_id:
			Profile ID
		:return:
			Profile or None if not found
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[ProfileEntity]:
		"""
		Get all profiles

		:return:
			List of all profiles
		"""
		pass

	@abstractmethod
	def delete(self, profile_id: int) -> None:
		"""
		Delete profile

		:param profile_id:
			Profile ID
		:return:
		"""
		pass
