from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.Item import Item
from src.domain.game.entities.ItemSet import ItemSet
from src.domain.game.entities.Propbit import Propbit
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.exceptions import InvalidRegexException


class ItemService:

	def __init__(
		self,
		item_repository: IItemRepository = Provide[Container.item_repository],
		item_set_repository: IItemSetRepository = Provide[Container.item_set_repository]
	):
		self._item_repository = item_repository
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
		sort_order: str = "asc",
		profile_id: int | None = None
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
		:param profile_id:
			Optional profile ID filter (shows only items in shop inventory for profile)
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
			item_id is not None,
			profile_id is not None
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
					sort_order=sort_order,
					profile_id=profile_id
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
