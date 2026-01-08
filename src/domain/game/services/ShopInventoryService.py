import typing

from dependency_injector.providers import Factory
from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.interfaces.ILocationShopFactory import ILocationShopFactory
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.interfaces.IShopInventoryService import IShopInventoryService


class ShopInventoryService(IShopInventoryService):

	def __init__(
		self,
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository],
		location_shop_factory: Factory[ILocationShopFactory] = Provide[Container.location_shop_factory.provider]
	):
		self._shop_inventory_repository = shop_inventory_repository
		self._location_shop_factory = location_shop_factory

	def get_shops_by_location(
		self,
		profile_id: int,
		group_by: ShopsGroupBy = ShopsGroupBy.LOCATION,
		types: typing.Iterable[ShopProductType] = None
	) -> dict[str, dict[str, list[Shop]]]:
		"""
		Get all shops grouped by location with enriched inventory data

		:param profile_id:
			Profile ID to filter inventory
		:param types:
			Types to select
		:param group_by:
			Group by given key
		:return:
			Dictionary mapping location_kb_id to location data with shops
		"""
		all_inventory = self._shop_inventory_repository.get_by_profile(profile_id, None)
		return self._location_shop_factory(products=all_inventory).produce(
			group_by=group_by,
			types=types
		)
