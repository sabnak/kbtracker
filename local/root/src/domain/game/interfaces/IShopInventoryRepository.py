import typing
from abc import ABC, abstractmethod
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType


class IShopInventoryRepository(ABC):

	@abstractmethod
	def create(self, inventory: ShopProduct) -> ShopProduct:
		"""
		Create new shop inventory entry

		:param inventory:
			Inventory entry to create
		:return:
			Created inventory entry
		"""
		pass

	@abstractmethod
	def get_by_profile(
		self,
		profile_id: int,
		product_types: typing.Iterable[ShopProductType] = None
	) -> list[ShopProduct]:
		"""
		Get all inventory entries for a profile, optionally filtered by type

		:param profile_id:
			Profile ID
		:param product_types:
			Optional inventory types filter
		:return:
			List of inventory entries
		"""
		pass

	@abstractmethod
	def get_by_entity(
		self,
		product_id: int,
		product_type: ShopProductType,
		profile_id: int
	) -> list[ShopProduct]:
		"""
		Get all shops where an entity is found for a profile

		:param product_id:
			Product ID
		:param product_type:
			Product type
		:param profile_id:
			Profile ID
		:return:
			List of inventory entries
		"""
		pass

	@abstractmethod
	def delete(self, product_id: int) -> None:
		"""
		Delete shop inventory entry

		:param product_id:
			Product ID
		:return:
		"""
		pass

	@abstractmethod
	def delete_by_profile(self, profile_id: int) -> None:
		"""
		Delete all shop inventory entries for a profile

		:param profile_id:
			Profile ID
		:return:
		"""
		pass
