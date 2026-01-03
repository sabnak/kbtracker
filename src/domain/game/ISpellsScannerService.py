from abc import ABC, abstractmethod

from src.domain.game.entities.Spell import Spell


class ISpellsScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, game_name: str) -> list[Spell]:
		"""
		Scan and import spells from game files

		:param game_id:
			Game ID
		:param game_name:
			Game name for file paths
		:return:
			List of created Spell entities
		"""
		pass
