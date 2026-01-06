import typing

import pydantic

from src.domain.app.entities.MetaName import MetaName
from src.domain.app.entities.Settings import Settings
from src.domain.app.interfaces.IMetaRepository import IMetaRepository, T
from src.domain.app.repositories.mappers.MetaMapper import MetaMapper
from src.domain.base.repositories.CrudRepository import CrudRepository, TEntity, TMapper


class MetaRepository(CrudRepository[pydantic.BaseModel, MetaMapper], IMetaRepository):

	_names_to_entities: dict[MetaName, typing.Type[T]] = {
		MetaName.SETTINGS: Settings
	}

	def get(self, name: MetaName) -> T:
		entity_type = self._names_to_entities[name]
		with self._session_factory() as session:
			mapper = session.query(MetaMapper).filter(
				MetaMapper.name == name.value
			).one_or_none()
			return entity_type(**mapper)

	def _entity_to_mapper(self, entity: TEntity) -> TMapper:
		raise NotImplementedError

	def _mapper_to_entity(self, mapper: TMapper) -> TEntity:
		raise NotImplementedError

	def _get_entity_type_name(self) -> str:
		raise NotImplementedError

	def _get_duplicate_identifier(self, entity: TEntity) -> str:
		raise NotImplementedError
