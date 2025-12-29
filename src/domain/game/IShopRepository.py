from abc import ABC, abstractmethod
from src.domain.game.entities.Shop import Shop


class IShopRepository(ABC):

	@abstractmethod
	def create(self, shop: Shop) -> Shop:
		"""
		Create new shop

		:param shop:
			Shops to create
		:return:
			Created shop with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, shop_id: int) -> Shop | None:
		"""
		Get shop by ID

		:param shop_id:
			Shop ID
		:return:
			Shops= or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: int) -> Shop | None:
		"""
		Get shop by game identifier

		:param kb_id:
			Game identifier
		:return:
			Shop or None if not found
		"""
		pass

	@abstractmethod
	def get_by_location_id(self, location_id: int) -> list[Shop]:
		"""
		Get all shops in a location

		:param location_id:
			Location ID
		:return:
			List of shops in the location
		"""
		pass

	@abstractmethod
	def list_by_game_id(self, game_id: int) -> list[Shop]:
		"""
		Get all shops for a specific game

		:param game_id:
			Game ID
		:return:
			List of shops for the game
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[Shop]:
		"""
		Get all shops

		:return:
			List of all shop
		"""
		pass

	@abstractmethod
	def create_batch(self, shops: list[Shop]) -> list[Shop]:
		"""
		Create multiple shops

		:param shops:
			Shops to create
		:return:
			Created shops with IDs
		"""
		pass
