from datetime import datetime

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.profile.IProfileRepository import IProfileRepository
from src.domain.profile.IProfileService import IProfileService
from src.domain.profile.entities.ProfileEntity import ProfileEntity


class ProfileService(IProfileService):

	def __init__(self, profile_repository: IProfileRepository = Provide[Container.profile_repository]):
		self._profile_repository = profile_repository

	def create_profile(self, name: str, game_version: str) -> ProfileEntity:
		"""
		Create new game profile

		:param name:
			Profile name
		:param game_version:
			Game version identifier
		:return:
			Created profile
		"""
		profile = ProfileEntity(
			id=0,
			name=name,
			game_version=game_version,
			created_at=datetime.utcnow()
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
