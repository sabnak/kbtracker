from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.game.IProfileRepository import IProfileRepository
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.repositories.mappers.ProfileMapper import ProfileMapper


class ProfilePostgresRepository(CrudRepository[ProfileEntity, ProfileMapper], IProfileRepository):

	def _entity_to_mapper(self, entity: ProfileEntity) -> ProfileMapper:
		"""
		Convert ProfileEntity to ProfileMapper

		:param entity:
			ProfileEntity to convert
		:return:
			ProfileMapper instance
		"""
		return ProfileMapper(
			name=entity.name,
			created_at=entity.created_at
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Profile"

	def _get_duplicate_identifier(self, entity: ProfileEntity) -> str:
		"""
		Get duplicate identifier for Profile

		:param entity:
			ProfileEntity
		:return:
			Identifier string
		"""
		return f"name={entity.name}"

	def create(self, profile: ProfileEntity) -> ProfileEntity:
		"""
		Create new profile

		:param profile:
			ProfileEntity to create
		:return:
			Created profile with database ID
		"""
		return self._create_single(profile)

	def get_by_id(self, profile_id: int) -> ProfileEntity | None:
		with self._get_session() as session:
			model = session.query(ProfileMapper).filter(
				ProfileMapper.id == profile_id
			).first()
			return self._mapper_to_entity(model) if model else None

	def list_all(self) -> list[ProfileEntity]:
		with self._get_session() as session:
			models = session.query(ProfileMapper).order_by(
				ProfileMapper.created_at.desc()
			).all()
			return [self._mapper_to_entity(m) for m in models]

	def delete(self, profile_id: int) -> None:
		"""
		Delete profile by ID

		:param profile_id:
			Profile ID to delete
		:return:
		"""
		with self._get_session() as session:
			session.query(ProfileMapper).filter(
				ProfileMapper.id == profile_id
			).delete()
			session.commit()

	def _mapper_to_entity(self, mapper: ProfileMapper) -> ProfileEntity:
		return ProfileEntity(**{
			"id": mapper.id,
			"name": mapper.name,
			"created_at": mapper.created_at
		})
