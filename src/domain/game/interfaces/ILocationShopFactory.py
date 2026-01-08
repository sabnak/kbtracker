from abc import ABC, abstractmethod

from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.entities.Shop import Shop


class ILocationShopFactory(ABC):

	@abstractmethod
	def produce(
		self,
		group_by: ShopsGroupBy = ShopsGroupBy.LOCATION
	) -> dict[str, dict[str, list[Shop]]]:
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
