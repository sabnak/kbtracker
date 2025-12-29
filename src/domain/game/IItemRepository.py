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
	def list_all(self) -> list[Item]:
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
	def list_by_game_id(
		self,
		game_id: int,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Item]:
		"""
		Get all items for a specific game

		:param game_id:
			Game ID
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of items for the game
		"""
		pass

	@abstractmethod
	def search_by_name_and_game(self, query: str, game_id: int) -> list[Item]:
		"""
		Search items by name for a specific game

		:param query:
			Search query
		:param game_id:
			Game ID
		:return:
			List of matching items for the game
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
		game_id: int,
		name_query: str | None = None,
		level: int | None = None,
		hint_regex: str | None = None,
		propbit: str | None = None,
		item_set_id: int | None = None,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Item]:
		"""
		Search items with multiple filter criteria using AND logic

		:param game_id:
			Game ID to filter by
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
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of items matching all provided criteria
		"""
		pass

	@abstractmethod
	def get_distinct_levels(self, game_id: int) -> list[int]:
		"""
		Get list of distinct level values for a game

		:param game_id:
			Game ID
		:return:
			Sorted list of distinct levels
		"""
		pass
