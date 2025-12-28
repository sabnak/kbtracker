from abc import ABC, abstractmethod
from src.domain.game.entities.Item import Item
from src.domain.game.entities.Object import Object
from src.domain.game.entities.Location import Location


class IGameScanner(ABC):

	@abstractmethod
	def scan_items(self, file_path: str) -> list[Item]:
		"""
		Scan items from game data file

		:param file_path:
			Path to game data file
		:return:
			List of items
		"""
		pass

	@abstractmethod
	def scan_objects(self, file_path: str) -> list[tuple[Object, Location]]:
		"""
		Scan objects and their locations from game data file

		:param file_path:
			Path to game data file
		:return:
			List of tuples (Object, Location)
		"""
		pass
