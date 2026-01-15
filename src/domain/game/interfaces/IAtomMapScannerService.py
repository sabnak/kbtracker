from abc import ABC, abstractmethod

from src.domain.game.entities.AtomMap import AtomMap


class IAtomMapScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, game_name: str) -> list[AtomMap]:
		pass
