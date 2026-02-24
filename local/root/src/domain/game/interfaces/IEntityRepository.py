import typing
from abc import ABC, abstractmethod

from src.domain.base.entities.BaseEntity import BaseEntity

TEntity = typing.TypeVar("TEntity", bound=BaseEntity)


class IEntityRepository(ABC, typing.Generic[TEntity]):

	@abstractmethod
	def create(self, atom_map: TEntity) -> TEntity:
		pass

	@abstractmethod
	def create_batch(self, atom_maps: list[TEntity]) -> list[TEntity]:
		pass

	@abstractmethod
	def get_by_id(self, atom_map_id: int) -> TEntity | None:
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> TEntity | None:
		pass

	@abstractmethod
	def list_all(self) -> list[TEntity]:
		pass

	@abstractmethod
	def get_by_ids(self, ids: typing.Iterable[int]) -> dict[int, TEntity]:
		"""
		Batch fetch entities by IDs

		:param ids:
			List of entities IDs
		:return:
			Dictionary mapping ID to TEntity
		"""
		pass
