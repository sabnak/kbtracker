from abc import ABC, abstractmethod
from src.domain.game.entities.Item import Item


class IItemRepository(ABC):

	@abstractmethod
	def create(self, item: Item) -> Item:
		"""
		Create new item

		:param item:
			Item to create
		:return:
			Created item with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, item_id: int) -> Item | None:
		"""
		Get item by ID

		:param item_id:
			Item ID
		:return:
			Item or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> Item | None:
		"""
		Get item by game identifier

		:param kb_id:
			Game identifier
		:return:
			Item or None if not found
		"""
		pass

	@abstractmethod
	def list_all(self, sort_by: str = "name", sort_order: str = "asc") -> list[Item]:
		"""
		Get all items

		:return:
			List of all items
		"""
		pass

	@abstractmethod
	def search_by_name(self, query: str) -> list[Item]:
		"""
		Search items by name

		:param query:
			Search query
		:return:
			List of matching items
		"""
		pass

	@abstractmethod
	def create_batch(self, items: list[Item]) -> list[Item]:
		"""
		Create multiple items

		:param items:
			Items to create
		:return:
			Created items with IDs
		"""
		pass

	@abstractmethod
	def get_by_kb_ids(self, kb_ids: list[str]) -> dict[str, Item]:
		"""
		Get multiple items by their kb_ids

		:param kb_ids:
			List of kb_id strings
		:return:
			Dictionary mapping kb_id to Item entity
		"""
		pass

	@abstractmethod
	def list_by_item_set_id(self, item_set_id: int) -> list[Item]:
		"""
		Get all items belonging to a specific item set

		:param item_set_id:
			Item set ID
		:return:
			List of items in the set
		"""
		pass

	@abstractmethod
	def search_with_filters(
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
	) -> list[Item]:
		"""
		Search items with multiple filter criteria using AND logic

		:param name_query:
			Optional name search (case-insensitive LIKE)
		:param level:
			Optional level filter (exact match)
		:param hint_regex:
			Optional PostgreSQL regex pattern for hint field
		:param propbit:
			Optional propbit value (matches if ANY propbit matches)
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
			List of items matching all provided criteria
		"""
		pass

	@abstractmethod
	def get_distinct_levels(self) -> list[int]:
		"""
		Get list of distinct level values

		:return:
			Sorted list of distinct levels
		"""
		pass

	@abstractmethod
	def get_by_ids(self, ids: list[int]) -> dict[int, Item]:
		"""
		Batch fetch items by IDs

		:param ids:
			List of item IDs
		:return:
			Dictionary mapping ID to Item
		"""
		pass
