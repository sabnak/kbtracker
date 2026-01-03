from datetime import datetime
import hashlib

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.IProfileRepository import IProfileRepository
from src.domain.game.IProfileService import IProfileService
from src.domain.game.entities.ProfileEntity import ProfileEntity


class ProfileService(IProfileService):

	def __init__(self, profile_repository: IProfileRepository = Provide[Container.profile_repository]):
		self._profile_repository = profile_repository

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
