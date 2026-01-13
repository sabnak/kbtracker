from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.Localization import Localization
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.game.repositories.mappers.LocalizationMapper import LocalizationMapper


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
			source=entity.source,
			tag=entity.tag
		)

	def _mapper_to_entity(self, mapper: LocalizationMapper) -> Localization:
		"""
		Convert LocalizationMapper to Localization entity

		:param mapper:
			LocalizationMapper to convert
		:return:
			Localization entity
		"""
		return PydanticEntityFactory.create_entity(Localization, mapper)

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
		return f"kb_id={entity.kb_id}"

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
		with self._get_session() as session:
			mapper = session.query(LocalizationMapper).filter(
				LocalizationMapper.id == localization_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Localization | None:
		"""
		Get localization by game identifier

		:param kb_id:
			Game identifier
		:return:
			Localization or None if not found
		"""
		with self._get_session() as session:
			mapper = session.query(LocalizationMapper).filter(
				LocalizationMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def search_by_text(self, query: str) -> list[Localization]:
		"""
		Search localization text (case-insensitive)

		:param query:
			Search query
		:return:
			List of matching localizations
		"""
		with self._get_session() as session:
			mappers = session.query(LocalizationMapper).filter(
				LocalizationMapper.text.ilike(f"%{query}%")
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def search_by_kb_id(self, pattern: str, use_regex: bool = False) -> list[Localization]:
		"""
		Search localizations by kb_id pattern using LIKE or regex

		:param pattern:
			kb_id pattern to search for (use % for LIKE wildcards, or regex pattern)
		:param use_regex:
			If True, use PostgreSQL regex matching (~), otherwise use LIKE
		:return:
			List of matching localizations
		"""
		with self._get_session() as session:
			if use_regex:
				mappers = session.query(LocalizationMapper).filter(
					LocalizationMapper.kb_id.op('~')(pattern)
				).all()
			else:
				mappers = session.query(LocalizationMapper).filter(
					LocalizationMapper.kb_id.like(pattern)
				).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def list_all(self, tag: str | None = None) -> list[Localization]:
		"""
		Get all localization entries

		:param tag:
			Optional tag filter
		:return:
			List of all localizations (filtered by tag if provided)
		"""
		with self._get_session() as session:
			query = session.query(LocalizationMapper)

			if tag is not None:
				query = query.filter(LocalizationMapper.tag == tag)

			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]
