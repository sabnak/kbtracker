import typing

from dependency_injector.providers import Factory
from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.interfaces.IShopFactory import IShopFactory
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.interfaces.IShopInventoryService import IShopInventoryService
from src.domain.game.services.shop_groupers.LocationShopGrouper import LocationShopGrouper
from src.domain.game.services.shop_groupers.ProductShopGrouper import ProductShopGrouper


class ShopInventoryService(IShopInventoryService):

	def __init__(
		self,
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository],
		shop_factory: Factory[IShopFactory] = Provide[Container.shop_factory.provider]
	):
		self._shop_inventory_repository = shop_inventory_repository
		self._shop_factory = shop_factory

	def get_shops(
		self,
		profile_id: int,
		group_by: ShopsGroupBy = ShopsGroupBy.LOCATION,
		types: typing.Iterable[ShopProductType] = None
	) -> dict[int | str, list[Shop]]:
		"""
		Get all shops grouped by specified criteria

		:param profile_id:
			Profile ID to filter inventory
		:param group_by:
			Group by strategy
		:param types:
			Types to select (reserved for future use)
		:return:
			Dictionary mapping group keys to lists of shops
		"""
		all_inventory = self._shop_inventory_repository.get_by_profile(profile_id, types)
		shops = self._shop_factory(products=all_inventory).produce()

		grouper = self._select_grouper(group_by)

		return grouper.group(shops)

	@staticmethod
	def _select_grouper(group_by: ShopsGroupBy):
		"""
		Select appropriate grouper based on group_by parameter

		:param group_by:
			Grouping strategy to use
		:return:
			Grouper instance
		"""
		if group_by == ShopsGroupBy.LOCATION:
			return LocationShopGrouper()
		elif group_by == ShopsGroupBy.ITEM:
			return ProductShopGrouper(ShopProductType.ITEM)
		elif group_by == ShopsGroupBy.SPELL:
			return ProductShopGrouper(ShopProductType.SPELL)
		elif group_by == ShopsGroupBy.UNIT:
			return ProductShopGrouper(ShopProductType.UNIT)
		else:
			raise ValueError(f"Unsupported group_by value: {group_by}")
