from abc import ABC, abstractmethod

from src.domain.game.entities.Shop import Shop


class IShopGrouper(ABC):

	@abstractmethod
	def group(self, shops: list[Shop]) -> dict[int | str, list[Shop]]:
		"""
		Group shops according to specific strategy

		:param shops:
			List of Shop entities to group
		:return:
			Dictionary mapping group keys to lists of shops
			Keys: int (product IDs) or str (location names)
		"""
		pass

