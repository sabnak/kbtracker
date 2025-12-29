from abc import ABC, abstractmethod
from src.domain.game.entities.ItemSet import ItemSet


class IItemSetRepository(ABC):

	@abstractmethod
	def create(self, item_set: ItemSet) -> ItemSet:
		"""
		Create new item set

		:param item_set:
			Item set to create
		:return:
			Created item set with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, item_set_id: int) -> ItemSet | None:
		"""
		Get item set by ID

		:param item_set_id:
			Item set ID
		:return:
			Item set or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str, game_id: int) -> ItemSet | None:
		"""
		Get item set by game identifier and game ID

		:param kb_id:
			Game identifier
		:param game_id:
			Game ID
		:return:
			Item set or None if not found
		"""
		pass

	@abstractmethod
	def list_by_game_id(self, game_id: int) -> list[ItemSet]:
		"""
		Get all item sets for a specific game

		:param game_id:
			Game ID
		:return:
			List of item sets for the game
		"""
		pass

	@abstractmethod
	def list_by_ids(self, item_set_ids: list[int]) -> list[ItemSet]:
		"""
		Get multiple item sets by their IDs

		:param item_set_ids:
			List of item set IDs
		:return:
			List of item sets
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[ItemSet]:
		"""
		Get all item sets

		:return:
			List of all item sets
		"""
		pass

	@abstractmethod
	def create_batch(self, item_sets: list[ItemSet]) -> list[ItemSet]:
		"""
		Create multiple item sets

		:param item_sets:
			Item sets to create
		:return:
			Created item sets with IDs
		"""
		pass
