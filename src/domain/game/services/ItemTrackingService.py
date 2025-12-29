from src.domain.game.entities.Item import Item
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopHasItem import ShopHasItem
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository


class ItemTrackingService:

	def __init__(
		self,
		item_repository: IItemRepository,
		location_repository: ILocationRepository,
		shop_repository: IShopRepository,
		shop_has_item_repository: IShopHasItemRepository
	):
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._shop_repository = shop_repository
		self._shop_has_item_repository = shop_has_item_repository

	def search_items(self, game_id: int, query: str) -> list[Item]:
		"""
		Search items by name for a specific game

		:param game_id:
			Game ID
		:param query:
			Search query
		:return:
			List of matching items
		"""
		if not query or query.strip() == "":
			return self._item_repository.list_by_game_id(game_id)
		return self._item_repository.search_by_name_and_game(query, game_id)

	def get_locations(self, game_id: int) -> list[Location]:
		"""
		Get all locations for a specific game

		:param game_id:
			Game ID
		:return:
			List of all locations
		"""
		return self._location_repository.list_by_game_id(game_id)

	def get_shops_by_location(self, location_id: int) -> list[Shop]:
		"""
		Get all shops in a location

		:param location_id:
			Location ID
		:return:
			List of shops
		"""
		return self._shop_repository.get_by_location_id(location_id)

	def link_item_to_shop(
		self,
		profile_id: int,
		item_id: int,
		shop_id: int,
		count: int
	) -> None:
		"""
		Link item to shop for a profile

		:param profile_id:
			Profile ID
		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:param count:
			Number of items available
		:return:
		"""
		link = ShopHasItem(
			item_id=item_id,
			shop_id=shop_id,
			profile_id=profile_id,
			count=count
		)
		self._shop_has_item_repository.create(link)

	def get_tracked_items(self, profile_id: int) -> list[dict]:
		"""
		Get all tracked items for a profile with location and shop info

		:param profile_id:
			Profile ID
		:return:
			List of dictionaries with item, shop, and location data
		"""
		links = self._shop_has_item_repository.get_by_profile(profile_id)

		result = []
		for link in links:
			item = self._item_repository.get_by_id(link.item_id)
			shop = self._shop_repository.get_by_id(link.shop_id)
			location = self._location_repository.get_by_id(shop.location_id) if shop else None

			result.append({
				"item": item,
				"shop": shop,
				"location": location,
				"count": link.count
			})

		return result

	def get_all_items_with_tracked_shops(
		self,
		profile_id: int,
		game_id: int
	) -> list[dict]:
		"""
		Get all items for a game with their tracked shops

		:param profile_id:
			Profile ID
		:param game_id:
			Game ID
		:return:
			List of items with tracked shop information
		"""
		all_items = self._item_repository.list_by_game_id(game_id)
		tracked_links = self._shop_has_item_repository.get_by_profile(profile_id)

		tracked_by_item = {}
		for link in tracked_links:
			if link.item_id not in tracked_by_item:
				tracked_by_item[link.item_id] = []

			shop = self._shop_repository.get_by_id(link.shop_id)
			location = None
			if shop:
				location = self._location_repository.get_by_id(shop.location_id)

			tracked_by_item[link.item_id].append({
				"shop": shop,
				"location": location,
				"count": link.count
			})

		result = []
		for item in all_items:
			tracked_shops = tracked_by_item.get(item.id, [])
			result.append({
				"item": item,
				"tracked_shops": tracked_shops
			})

		return result

	def get_shops_grouped_by_location(self, game_id: int) -> list[dict]:
		"""
		Get shops grouped by location for a specific game

		:param game_id:
			Game ID
		:return:
			List of locations with their shops
		"""
		locations = self._location_repository.list_by_game_id(game_id)

		result = []
		for location in locations:
			shops = self._shop_repository.get_by_location_id(location.id)
			result.append({
				"location": location,
				"shops": shops
			})

		return result

	def update_item_shop_count(
		self,
		profile_id: int,
		item_id: int,
		shop_id: int,
		count: int
	) -> None:
		"""
		Update count for item-shop tracking

		:param profile_id:
			Profile ID
		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:param count:
			New count value
		:return:
		"""
		self._shop_has_item_repository.update_count(
			item_id=item_id,
			shop_id=shop_id,
			profile_id=profile_id,
			new_count=count
		)

	def remove_item_from_shop(
		self,
		profile_id: int,
		item_id: int,
		shop_id: int
	) -> None:
		"""
		Remove item tracking from a shop

		:param profile_id:
			Profile ID
		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:return:
		"""
		self._shop_has_item_repository.delete(
			item_id=item_id,
			shop_id=shop_id,
			profile_id=profile_id
		)
