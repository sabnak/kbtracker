from abc import ABC, abstractmethod

from src.domain.game.entities.Item import Item
from src.domain.game.entities.ItemSet import ItemSet


class IItemsAndSetsScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, game_name: str) -> tuple[list[Item], list[ItemSet]]:
		"""
		Scan and import items and item sets from game files

		:param game_id:
			Game ID to scan
		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:return:
			Tuple of (items, item_sets) with database IDs
		"""
		pass
