from typing import Any

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.exceptions import EntityNotFoundException
from src.domain.game.IAtomMapRepository import IAtomMapRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IProfileGameDataSyncerService import IProfileGameDataSyncerService
from src.domain.game.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.ISpellRepository import ISpellRepository
from src.domain.game.IUnitRepository import IUnitRepository
from src.domain.game.entities.ShopInventory import ShopInventory
from src.domain.game.entities.ShopInventoryType import ShopInventoryType


class ProfileGameDataSyncerService(IProfileGameDataSyncerService):

	def __init__(
		self,
		item_repository: IItemRepository = Provide[Container.item_repository],
		spell_repository: ISpellRepository = Provide[Container.spell_repository],
		unit_repository: IUnitRepository = Provide[Container.unit_repository],
		atom_map_repository: IAtomMapRepository = Provide[Container.atom_map_repository],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository]
	):
		self._item_repository = item_repository
		self._spell_repository = spell_repository
		self._unit_repository = unit_repository
		self._atom_map_repository = atom_map_repository
		self._shop_inventory_repository = shop_inventory_repository

	def sync(
		self,
		data: dict[str, dict[str, list[dict[str, Any]]]],
		profile_id: int
	) -> dict[str, int]:
		"""
		Sync parsed shop inventory data to database

		:param data:
			Parsed shop data from parse() method
		:param profile_id:
			Profile ID to associate inventories with
		:return:
			Dictionary with counts
		:raises EntityNotFoundException:
			If any shop, item, spell, or unit not found in database
		"""
		counts = {"items": 0, "spells": 0, "units": 0, "garrison": 0}

		for shop_kb_id, inventories in data.items():
			atom_map = self._atom_map_repository.get_by_kb_id(shop_kb_id)

			if not atom_map:
				raise EntityNotFoundException("AtomMap", shop_kb_id)

			counts["items"] += self._sync_items(inventories['items'], atom_map.id, profile_id)
			counts["spells"] += self._sync_spells(inventories['spells'], atom_map.id, profile_id)
			counts["units"] += self._sync_units(inventories['units'], atom_map.id, profile_id)
			counts["garrison"] += self._sync_garrison(inventories['garrison'], atom_map.id, profile_id)

		return counts

	def _sync_items(
		self,
		items: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int
	) -> int:
		"""
		Sync item inventories

		:param items:
			Item inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:return:
			Number of items synced
		"""
		count = 0
		for item_data in items:
			kb_id = item_data['name']
			item = self._item_repository.get_by_kb_id(kb_id)

			if not item:
				raise EntityNotFoundException("Item", kb_id)

			inventory = ShopInventory(
				entity_id=item.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopInventoryType.ITEM,
				count=item_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_spells(
		self,
		spells: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int
	) -> int:
		"""
		Sync spell inventories

		:param spells:
			Spell inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:return:
			Number of spells synced
		"""
		count = 0
		for spell_data in spells:
			kb_id = spell_data['name'][6:]  # spell_
			spell = self._spell_repository.get_by_kb_id(kb_id)

			if not spell:
				raise EntityNotFoundException("Spell", kb_id)

			inventory = ShopInventory(
				entity_id=spell.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopInventoryType.SPELL,
				count=spell_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_units(
		self,
		units: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int
	) -> int:
		"""
		Sync unit inventories

		:param units:
			Unit inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:return:
			Number of units synced
		"""
		count = 0
		for unit_data in units:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				raise EntityNotFoundException("Unit", kb_id)

			inventory = ShopInventory(
				entity_id=unit.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopInventoryType.UNIT,
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_garrison(
		self,
		garrison: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int
	) -> int:
		"""
		Sync garrison inventories

		:param garrison:
			Garrison inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:return:
			Number of garrison units synced
		"""
		count = 0
		for unit_data in garrison:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				raise EntityNotFoundException("Unit", kb_id)

			inventory = ShopInventory(
				entity_id=unit.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopInventoryType.GARRISON,
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count
