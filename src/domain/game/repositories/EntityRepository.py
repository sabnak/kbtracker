import typing

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.base.repositories.mappers.EntityMapper import EntityMapper
from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.interfaces.IEntityRepository import IEntityRepository, TEntity
from src.domain.game.interfaces.ILocFactory import ILocFactory
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.base.repositories.CrudRepository import CrudRepository


TMapper = typing.TypeVar("TMapper", bound=EntityMapper)


class EntityRepository(CrudRepository[TEntity, TMapper], IEntityRepository[TEntity]):

	def __init__(
		self,
		entity_type: typing.Type[BaseEntity],
		mapper_type: typing.Type[EntityMapper],
		loc_pattern: str,
		loc_factory: ILocFactory = Provide[Container.loc_factory],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		super().__init__()
		self._entity_type = entity_type
		self._mapper_type = mapper_type
		self._loc_pattern = loc_pattern
		self._loc_factory = loc_factory
		self._localization_repository = localization_repository

	def _entity_to_mapper(self, entity: TEntity) -> TMapper:
		return self._mapper_type(kb_id=entity.kb_id)

	def _mapper_to_entity(self, mapper: TMapper) -> TEntity:
		loc = self._fetch_loc(mapper.kb_id)

		return self._entity_type(id=mapper.id, kb_id=mapper.kb_id, loc=loc)

	def _get_entity_type_name(self) -> str:
		return self._entity_type.__class__.__name__

	def _get_duplicate_identifier(self, entity: TEntity) -> str:
		return f"kb_id={entity.kb_id}"

	def create(self, entity: TEntity) -> TEntity:
		return self._create_single(entity)

	def create_batch(self, entities: list[TEntity]) -> list[TEntity]:
		return self._create_batch(entities)

	def get_by_id(self, entity_id: int) -> TEntity | None:
		with self._get_session() as session:
			mapper = session.query(self._mapper_type).filter(
				self._mapper_type.id == entity_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> TEntity | None:
		with self._get_session() as session:
			mapper = session.query(self._mapper_type).filter(
				self._mapper_type.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[TEntity]:
		with self._get_session() as session:
			mappers = session.query(self._mapper_type).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def get_by_ids(self, ids: list[int]) -> dict[int, TEntity]:
		"""
		Batch fetch entities by IDs

		:param ids:
			List of entities IDs
		:return:
			Dictionary mapping ID to Entity
		"""
		if not ids:
			return {}

		with self._get_session() as session:
			mappers = session.query(self._mapper_type).filter(self._mapper_type.id.in_(ids)).all()

			result = {}
			for mapper in mappers:
				entity = self._mapper_to_entity(mapper)
				result[entity.id] = entity

			return result

	def _fetch_loc(self, kb_id: str) -> LocStrings | None:
		pattern = self._loc_pattern.format(kb_id)
		localizations = self._localization_repository.search_by_kb_id(pattern, use_regex=False)

		if not localizations:
			return None

		return self._loc_factory.create_from_localizations(localizations)
