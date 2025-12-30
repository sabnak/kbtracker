from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.Localization import Localization
from src.domain.game.entities.LocalizationType import LocalizationType
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.repositories.mappers.LocalizationMapper import LocalizationMapper
from src.domain.exceptions import InvalidLocalizationTypeException


class LocalizationRepository(
	CrudRepository[Localization, LocalizationMapper],
	ILocalizationRepository
):

	def _entity_to_mapper(self, entity: Localization) -> LocalizationMapper:
		"""
		Convert Localization entity to LocalizationMapper

		:param entity:
			Localization entity to convert
		:return:
			LocalizationMapper instance
		"""
		return LocalizationMapper(
			kb_id=entity.kb_id,
			text=entity.text,
			type=entity.type.value
		)

	def _mapper_to_entity(self, mapper: LocalizationMapper) -> Localization:
		"""
		Convert LocalizationMapper to Localization entity

		:param mapper:
			LocalizationMapper to convert
		:return:
			Localization entity
		:raises InvalidLocalizationTypeException:
			When mapper contains invalid type value
		"""
		type_enum = self._convert_type_to_enum(mapper.type)

		return Localization(
			id=mapper.id,
			kb_id=mapper.kb_id,
			text=mapper.text,
			type=type_enum
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Localization"

	def _get_duplicate_identifier(self, entity: Localization) -> str:
		"""
		Get duplicate identifier for Localization

		:param entity:
			Localization entity
		:return:
			Identifier string
		"""
		return f"kb_id={entity.kb_id}, type={entity.type.value}"

	def _convert_type_to_enum(self, type_str: str) -> LocalizationType:
		"""
		Convert string to LocalizationType enum

		:param type_str:
			Type string value from database
		:return:
			LocalizationType enum value
		:raises InvalidLocalizationTypeException:
			When type_str is invalid
		"""
		valid_values = [t.value for t in LocalizationType]

		try:
			return LocalizationType(type_str)
		except ValueError as e:
			raise InvalidLocalizationTypeException(
				invalid_value=type_str,
				valid_values=valid_values,
				original_exception=e
			)

	def create(self, localization: Localization) -> Localization:
		"""
		Create new localization entry

		:param localization:
			Localization entity to create
		:return:
			Created localization with database ID
		"""
		return self._create_single(localization)

	def create_batch(
		self,
		localizations: list[Localization]
	) -> list[Localization]:
		"""
		Create multiple localization entries

		:param localizations:
			List of localization entities to create
		:return:
			List of created localizations with database IDs
		"""
		return self._create_batch(localizations)

	def get_by_id(self, localization_id: int) -> Localization | None:
		"""
		Get localization by database ID

		:param localization_id:
			Localization ID
		:return:
			Localization or None if not found
		"""
		with self._session_factory() as session:
			mapper = session.query(LocalizationMapper).filter(
				LocalizationMapper.id == localization_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id_and_type(
		self,
		kb_id: str,
		type: LocalizationType
	) -> Localization | None:
		"""
		Get localization by composite unique key

		:param kb_id:
			Game identifier
		:param type:
			Localization type
		:return:
			Localization or None if not found
		"""
		with self._session_factory() as session:
			mapper = session.query(LocalizationMapper).filter(
				LocalizationMapper.kb_id == kb_id,
				LocalizationMapper.type == type.value
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_by_type(self, type: LocalizationType) -> list[Localization]:
		"""
		Get all localizations of a specific type

		:param type:
			Localization type
		:return:
			List of localizations of the specified type
		"""
		with self._session_factory() as session:
			mappers = session.query(LocalizationMapper).filter(
				LocalizationMapper.type == type.value
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def list_by_kb_id(self, kb_id: str) -> list[Localization]:
		"""
		Get all localizations for a specific kb_id

		:param kb_id:
			Game identifier
		:return:
			List of localizations with the specified kb_id
		"""
		with self._session_factory() as session:
			mappers = session.query(LocalizationMapper).filter(
				LocalizationMapper.kb_id == kb_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def search_by_text(
		self,
		query: str,
		type: LocalizationType | None = None
	) -> list[Localization]:
		"""
		Search localization text with optional type filter

		:param query:
			Search query (case-insensitive)
		:param type:
			Optional localization type filter
		:return:
			List of matching localizations
		"""
		with self._session_factory() as session:
			q = session.query(LocalizationMapper).filter(
				LocalizationMapper.text.ilike(f"%{query}%")
			)

			if type is not None:
				q = q.filter(LocalizationMapper.type == type.value)

			mappers = q.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def list_all(self) -> list[Localization]:
		"""
		Get all localization entries

		:return:
			List of all localizations
		"""
		with self._session_factory() as session:
			mappers = session.query(LocalizationMapper).all()
			return [self._mapper_to_entity(m) for m in mappers]
