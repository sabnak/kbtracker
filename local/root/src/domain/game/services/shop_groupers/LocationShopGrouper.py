from src.domain.game.interfaces.IShopGrouper import IShopGrouper
from src.domain.game.entities.Shop import Shop


class LocationShopGrouper(IShopGrouper):

	def group(self, shops: list[Shop]) -> dict[str, list[Shop]]:
		"""
		Group shops by location name

		:param shops:
			List of Shop entities
		:return:
			Dictionary mapping location_name to list of shops
		"""
		grouped = {}
		for shop in shops:
			location_name = shop.location_name
			if location_name not in grouped:
				grouped[location_name] = []
			grouped[location_name].append(shop)

		self._sort_shops_within_locations(grouped)

		return dict(sorted(grouped.items(), key=lambda x: x[0]))

	def _sort_shops_within_locations(self, grouped: dict) -> None:
		"""
		Sort shops within each location

		:param grouped:
			Dictionary of grouped shops (modified in place)
		"""
		for location_name in grouped:
			grouped[location_name].sort(
				key=lambda s: (
					s.shop_loc.name if s.shop_loc and s.shop_loc.name
					else s.shop_loc.hint if s.shop_loc and s.shop_loc.hint
					else s.shop_kb_id
				)
			)

