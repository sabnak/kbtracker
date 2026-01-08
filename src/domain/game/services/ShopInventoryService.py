from dependency_injector.providers import Factory
from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.interfaces.ILocationShopFactory import ILocationShopFactory
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository


class ShopInventoryService:

	def __init__(
		self,
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository],
		location_shop_factory: Factory[ILocationShopFactory] = Provide[Container.location_shop_factory.provider]
	):
		self._shop_inventory_repository = shop_inventory_repository
		self._location_shop_factory = location_shop_factory

	def get_shops_by_location(self, profile_id: int) -> dict[str, dict]:
		"""
		Get all shops grouped by location with enriched inventory data

		:param profile_id:
			Profile ID to filter inventory
		:return:
			Dictionary mapping location_kb_id to location data with shops
		"""
		all_inventory = self._shop_inventory_repository.get_by_profile(profile_id, None)
		return self._location_shop_factory(products=all_inventory).produce()
