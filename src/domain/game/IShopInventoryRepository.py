from abc import ABC, abstractmethod
from src.domain.game.entities.ShopInventory import ShopInventory


class IShopInventoryRepository(ABC):

	@abstractmethod
	def create(self, inventory: ShopInventory) -> ShopInventory:
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
		type: str | None = None
	) -> list[ShopInventory]:
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
		type: str,
		profile_id: int
	) -> list[ShopInventory]:
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
		type: str,
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
		type: str,
		atom_map_id: int,
		profile_id: int,
		new_count: int
	) -> ShopInventory:
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
