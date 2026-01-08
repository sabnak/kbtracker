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
		type: ShopProductType | None = None
	) -> list[ShopProduct]:
		"""
		Get all inventory entries for a profile, optionally filtered by type

		:param profile_id:
			Profile ID
		:param type:
			Optional inventory type filter
		:return:
			List of inventory entries
		"""
		pass

	@abstractmethod
	def get_by_entity(
		self,
		entity_id: int,
		type: ShopProductType,
		profile_id: int
	) -> list[ShopProduct]:
		"""
		Get all shops where an entity is found for a profile

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param profile_id:
			Profile ID
		:return:
			List of inventory entries
		"""
		pass

	@abstractmethod
	def delete(
		self,
		entity_id: int,
		type: ShopProductType,
		atom_map_id: int,
		profile_id: int
	) -> None:
		"""
		Delete shop inventory entry

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
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

	@abstractmethod
	def update_count(
		self,
		entity_id: int,
		type: ShopProductType,
		atom_map_id: int,
		profile_id: int,
		new_count: int
	) -> ShopProduct:
		"""
		Update count for shop inventory entry

		:param entity_id:
			Entity ID
		:param type:
			Entity type
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param new_count:
			New count value
		:return:
			Updated inventory entry
		"""
		pass
