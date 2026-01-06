from abc import ABC, abstractmethod

from src.domain.game.entities.Unit import Unit


class IUnitsScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, game_name: str) -> list[Unit]:
		"""
		Scan and import units from game files

		:param game_id:
			Game ID
		:param game_name:
			Game name for file paths
		:return:
			List of created Unit entities
		"""
		pass
