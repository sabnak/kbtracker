from abc import ABC, abstractmethod

from src.domain.game.entities.AtomMap import AtomMap


class IAtomMapRepository(ABC):

	@abstractmethod
	def create(self, atom_map: AtomMap) -> AtomMap:
		pass

	@abstractmethod
	def create_batch(self, atom_maps: list[AtomMap]) -> list[AtomMap]:
		pass

	@abstractmethod
	def get_by_id(self, atom_map_id: int) -> AtomMap | None:
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> AtomMap | None:
		pass

	@abstractmethod
	def list_all(self) -> list[AtomMap]:
		pass
