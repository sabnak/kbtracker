from src.domain.game.interfaces.IShopGrouper import IShopGrouper
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopProductType import ShopProductType


class ProductShopGrouper(IShopGrouper):

	def __init__(self, product_type: ShopProductType):
		"""
		Initialize product shop grouper

		:param product_type:
			Type of product to group by (ITEM, SPELL, UNIT, GARRISON)
		"""
		self._product_type = product_type

	def group(self, shops: list[Shop]) -> dict[int, list[Shop]]:
		"""
		Group shops by product ID they sell

		:param shops:
			List of Shop entities
		:return:
			Dictionary mapping product_id to list of shops selling it
		"""
		grouped = {}

		for shop in shops:
			product_ids = self._extract_product_ids(shop)
			for product_id in product_ids:
				if product_id not in grouped:
					grouped[product_id] = []
				grouped[product_id].append(shop)

		return dict(sorted(grouped.items()))

	def _extract_product_ids(self, shop: Shop) -> set[int]:
		"""
		Extract product IDs from shop based on product type

		:param shop:
			Shop entity
		:return:
			Set of product IDs found in shop
		"""
		product_ids = set()

		if self._product_type == ShopProductType.ITEM:
			for shop_item in shop.inventory.items:
				product_ids.add(shop_item.item.id)

		elif self._product_type == ShopProductType.SPELL:
			for shop_spell in shop.inventory.spells:
				product_ids.add(shop_spell.spell.id)

		elif self._product_type == ShopProductType.UNIT:
			for shop_unit in shop.inventory.units:
				product_ids.add(shop_unit.unit.id)

		elif self._product_type == ShopProductType.GARRISON:
			for garrison_unit in shop.inventory.garrison:
				product_ids.add(garrison_unit.unit.id)

		return product_ids

