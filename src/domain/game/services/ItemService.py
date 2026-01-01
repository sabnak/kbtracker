from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.Item import Item
from src.domain.game.entities.ItemSet import ItemSet
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Propbit import Propbit
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopHasItem import ShopHasItem
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.exceptions import InvalidRegexException


class ItemService:

	def __init__(
		self,
		item_repository: IItemRepository = Provide[Container.item_repository],
		location_repository: ILocationRepository = Provide[Container.location_repository],
		shop_repository: IShopRepository = Provide[Container.shop_repository],
		shop_has_item_repository: IShopHasItemRepository = Provide[Container.shop_has_item_repository],
		item_set_repository: IItemSetRepository = Provide[Container.item_set_repository]
	):
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._shop_repository = shop_repository
		self._shop_has_item_repository = shop_has_item_repository
		self._item_set_repository = item_set_repository

	def search_items(self, query: str) -> list[Item]:
		"""
		Search items by name

		:param query:
			Search query
		:return:
			List of matching items
		"""
		if not query or query.strip() == "":
			return self._item_repository.list_all()
		return self._item_repository.search_by_name(query)

	def get_items_with_sets(
		self,
		name_query: str | None = None,
		level: int | None = None,
		hint_regex: str | None = None,
		propbit: str | None = None,
		item_set_id: int | None = None,
		item_id: int | None = None,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[dict]:
		"""
		Get items with their set information using multiple filters

		:param name_query:
			Optional name search query
		:param level:
			Optional level filter
		:param hint_regex:
			Optional regex pattern for hint
		:param propbit:
			Optional propbit type filter
		:param item_set_id:
			Optional item set ID filter
		:param item_id:
			Optional item ID filter
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of dictionaries with item and set data
		"""
		# Check if any filter is provided
		has_filters = any([
			name_query,
			level is not None,
			hint_regex,
			propbit,
			item_set_id is not None,
			item_id is not None
		])

		# Get items - use advanced search if filters, otherwise all items
		try:
			if has_filters:
				items = self._item_repository.search_with_filters(
					name_query=name_query,
					level=level,
					hint_regex=hint_regex,
					propbit=propbit,
					item_set_id=item_set_id,
					item_id=item_id,
					sort_by=sort_by,
					sort_order=sort_order
				)
			else:
				items = self._item_repository.list_all(
					sort_by=sort_by,
					sort_order=sort_order
				)
		except Exception as e:
			# Check if it's a regex error (PostgreSQL will throw specific error)
			if "invalid regular expression" in str(e).lower():
				raise InvalidRegexException(hint_regex or "", e)
			raise

		# Collect unique item_set_ids
		set_ids = {item.item_set_id for item in items if item.item_set_id is not None}

		# Batch fetch all sets
		sets_map = {}
		if set_ids:
			sets = self._item_set_repository.list_by_ids(list(set_ids))
			sets_map = {s.id: s for s in sets}

		# Fetch items for each set
		set_items_map = {}
		for set_id in set_ids:
			set_items_map[set_id] = self._item_repository.list_by_item_set_id(set_id)

		# Collect all tier kb_ids
		all_tier_kb_ids = set()
		for item in items:
			if item.tiers:
				all_tier_kb_ids.update(item.tiers)

		# Batch fetch all tier items
		tier_items_by_kb_id = {}
		if all_tier_kb_ids:
			tier_items_by_kb_id = self._item_repository.get_by_kb_ids(list(all_tier_kb_ids))

		# Build enriched result
		result = []
		for item in items:
			item_data = {
				"item": item,
				"item_set": None,
				"set_items": [],
				"tier_items": []
			}

			if item.item_set_id and item.item_set_id in sets_map:
				item_data["item_set"] = sets_map[item.item_set_id]
				item_data["set_items"] = set_items_map.get(item.item_set_id, [])

			# Build ordered tier items list
			if item.tiers and len(item.tiers) > 1:
				tier_items = []
				for tier_kb_id in item.tiers:
					if tier_kb_id in tier_items_by_kb_id:
						tier_items.append(tier_items_by_kb_id[tier_kb_id])
				item_data["tier_items"] = tier_items

			result.append(item_data)

		return result

	def get_locations(self) -> list[Location]:
		"""
		Get all locations

		:return:
			List of all locations
		"""
		return self._location_repository.list_all()

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

	def get_all_items_with_tracked_shops(self, profile_id: int) -> list[dict]:
		"""
		Get all items with their tracked shops

		:param profile_id:
			Profile ID
		:return:
			List of items with tracked shop information
		"""
		all_items = self._item_repository.list_all()
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

	def get_shops_grouped_by_location(self) -> list[dict]:
		"""
		Get shops grouped by location

		:return:
			List of locations with their shops
		"""
		locations = self._location_repository.list_all()

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

	def get_available_levels(self) -> list[int]:
		"""
		Get all distinct item levels

		:return:
			Sorted list of levels
		"""
		return self._item_repository.get_distinct_levels()

	def get_available_propbits(self) -> list[str]:
		"""
		Get all available propbit types

		:return:
			List of propbit string values
		"""
		return [propbit.value for propbit in Propbit]

	def get_available_item_sets(self) -> list[ItemSet]:
		"""
		Get all item sets

		:return:
			List of item sets
		"""
		return self._item_set_repository.list_all()
