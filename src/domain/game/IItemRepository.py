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
	def list_by_game_id(self, game_id: int) -> list[Item]:
		"""
		Get all items for a specific game

		:param game_id:
			Game ID
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
