from abc import ABC, abstractmethod

from src.domain.game.entities.ShopProduct import ShopProduct


class ILocationShopFactory(ABC):

	@abstractmethod
	def produce(self) -> dict[str, dict]:
		"""
		Transform products into shops grouped by location

		:return:
			Dictionary mapping location_kb_id to location data:
			{
				"location_kb_id": {
					"name": "Location Name",
					"shops": [Shop, Shop, ...]
				}
			}
		"""
		pass
