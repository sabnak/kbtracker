from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.exceptions import EntityNotFoundException
from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.entities.ProfileEntity import ProfileEntity
from src.domain.game.entities.CorruptedProfileData import CorruptedProfileData
from src.domain.game.repositories.mappers.ProfileMapper import ProfileMapper
from src.domain.app.repositories.GameRepository import GameRepository


class ProfilePostgresRepository(CrudRepository[ProfileEntity, ProfileMapper], IProfileRepository):

	def _entity_to_mapper(self, entity: ProfileEntity) -> ProfileMapper:
		"""
		Convert ProfileEntity to ProfileMapper

		:param entity:
			ProfileEntity to convert
		:return:
			ProfileMapper instance
		"""
		corrupted_data_json = None
		if entity.last_corrupted_data:
			corrupted_data_json = entity.last_corrupted_data.model_dump()

		game_id = entity.game.id if entity.game else None

		return ProfileMapper(
			name=entity.name,
			hash=entity.hash,
			full_name=entity.full_name,
			save_dir=entity.save_dir,
			created_at=entity.created_at,
			last_scan_time=entity.last_scan_time,
			last_save_timestamp=entity.last_save_timestamp,
			last_corrupted_data=corrupted_data_json,
			is_auto_scan_enabled=entity.is_auto_scan_enabled,
			game_id=game_id
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

	def update(self, profile: ProfileEntity) -> ProfileEntity:
		"""
		Update existing profile

		:param profile:
			ProfileEntity to update
		:return:
			Updated profile
		"""
		with self._get_session() as session:
			mapper = session.query(ProfileMapper).filter(
				ProfileMapper.id == profile.id
			).first()

			if not mapper:
				raise EntityNotFoundException("Profile", profile.id)

			mapper.name = profile.name
			mapper.hash = profile.hash
			mapper.full_name = profile.full_name
			mapper.save_dir = profile.save_dir
			mapper.last_scan_time = profile.last_scan_time
			mapper.last_save_timestamp = profile.last_save_timestamp
			mapper.is_auto_scan_enabled = profile.is_auto_scan_enabled
			mapper.game_id = profile.game.id if profile.game else mapper.game_id

			if profile.last_corrupted_data:
				mapper.last_corrupted_data = profile.last_corrupted_data.model_dump()
			else:
				mapper.last_corrupted_data = None

			session.commit()
			session.refresh(mapper)

			return self._mapper_to_entity(mapper)

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
		corrupted_data = None
		if mapper.last_corrupted_data:
			corrupted_data = CorruptedProfileData(**mapper.last_corrupted_data)

		return PydanticEntityFactory.create_entity(
			ProfileEntity,
			mapper,
			last_corrupted_data=corrupted_data
		)
