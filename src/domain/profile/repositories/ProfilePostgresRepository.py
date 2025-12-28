from sqlalchemy.orm import Session

from src.domain.profile.IProfileRepository import IProfileRepository
from src.domain.profile.entities.ProfileEntity import ProfileEntity
from src.domain.profile.repositories.mappers.ProfileMapper import ProfileMapper


class ProfilePostgresRepository(IProfileRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, profile: ProfileEntity) -> ProfileEntity:
		model = ProfileMapper(
			name=profile.name,
			game_version=profile.game_version,
			created_at=profile.created_at
		)
		self._session.add(model)
		self._session.commit()
		self._session.refresh(model)
		return self._mapper_to_entity(model)

	def get_by_id(self, profile_id: int) -> ProfileEntity | None:
		model = self._session.query(ProfileMapper).filter(
			ProfileMapper.id == profile_id
		).first()
		return self._mapper_to_entity(model) if model else None

	def list_all(self) -> list[ProfileEntity]:
		models = self._session.query(ProfileMapper).order_by(
			ProfileMapper.created_at.desc()
		).all()
		return [self._mapper_to_entity(m) for m in models]

	def delete(self, profile_id: int) -> None:
		self._session.query(ProfileMapper).filter(
			ProfileMapper.id == profile_id
		).delete()
		self._session.commit()

	@staticmethod
	def _mapper_to_entity(mapper: ProfileMapper) -> ProfileEntity:
		return ProfileEntity(**{
			"id": mapper.id,
			"name": mapper.name,
			"game_version": mapper.game_version,
			"created_at": mapper.created_at
		})
