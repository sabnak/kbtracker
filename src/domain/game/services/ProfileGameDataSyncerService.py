import typing
from dataclasses import dataclass
from typing import Any

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.interfaces.IAtomMapRepository import IAtomMapRepository
from src.domain.game.interfaces.IItemRepository import IItemRepository
from src.domain.game.interfaces.IProfileGameDataSyncerService import IProfileGameDataSyncerService
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.interfaces.ISpellRepository import ISpellRepository
from src.domain.game.interfaces.IUnitRepository import IUnitRepository
from src.domain.game.dto.ProfileSyncResult import ProfileSyncResult
from src.domain.game.entities.CorruptedProfileData import CorruptedProfileData
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType


@dataclass
class _SyncItemResult:
	count: int
	missing_kb_ids: list[str]


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
		data: list[dict[str, typing.Any]],
		profile_id: int
	) -> ProfileSyncResult:
		"""
		Sync parsed shop inventory data to database

		:param data:
			Parsed shop data from parse() method
		:param profile_id:
			Profile ID to associate inventories with
		:return:
			ProfileSyncResult with counts and corrupted data
		"""
		counts = {"items": 0, "spells": 0, "units": 0, "garrison": 0}
		missing_shops: list[str] = []
		missing_items: list[str] = []
		missing_spells: list[str] = []
		missing_units: list[str] = []

		for shop_data in data:
			atom_map = None
			if shop_data['itext']:
				shop_kb_id = shop_data['itext']
				atom_map = self._atom_map_repository.get_by_kb_id(shop_kb_id)
			else:
				# We will ignore such shops for now
				shop_kb_id = f"actor_system_{shop_data['actor']}_name"

			inventory = shop_data['inventory']

			if not atom_map:
				missing_shops.append(shop_kb_id)
				continue

			item_result = self._sync_items(inventory['items'], atom_map.id, profile_id, shop_kb_id)
			counts["items"] += item_result.count
			missing_items.extend(item_result.missing_kb_ids)

			spell_result = self._sync_spells(inventory['spells'], atom_map.id, profile_id, shop_kb_id)
			counts["spells"] += spell_result.count
			missing_spells.extend(spell_result.missing_kb_ids)

			unit_result = self._sync_units(inventory['units'], atom_map.id, profile_id, shop_kb_id)
			counts["units"] += unit_result.count
			missing_units.extend(set(unit_result.missing_kb_ids))

			garrison_result = self._sync_garrison(inventory['garrison'], atom_map.id, profile_id, shop_kb_id)
			counts["garrison"] += garrison_result.count
			missing_units.extend(garrison_result.missing_kb_ids)

		corrupted_data = self._build_corrupted_data(
			shops=missing_shops,
			items=missing_items,
			spells=missing_spells,
			units=missing_units
		)

		return ProfileSyncResult(
			items=counts["items"],
			spells=counts["spells"],
			units=counts["units"],
			garrison=counts["garrison"],
			corrupted_data=corrupted_data
		)

	def _sync_items(
		self,
		items: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int,
		atom_kb_id: str
	) -> _SyncItemResult:
		"""
		Sync item inventories

		:param items:
			Item inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param atom_kb_id:
			Shop KB ID for context
		:return:
			Sync result with count and missing KB IDs
		"""
		count = 0
		missing_kb_ids: list[str] = []

		for item_data in items:
			kb_id = item_data['name']
			item = self._item_repository.get_by_kb_id(kb_id)

			if not item:
				missing_kb_ids.append(kb_id)
				continue

			inventory = ShopProduct(
				entity_id=item.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopProductType.ITEM,
				count=item_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return _SyncItemResult(count=count, missing_kb_ids=missing_kb_ids)

	def _sync_spells(
		self,
		spells: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int,
		atom_kb_id: str
	) -> _SyncItemResult:
		"""
		Sync spell inventories

		:param spells:
			Spell inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param atom_kb_id:
			Shop KB ID for context
		:return:
			Sync result with count and missing KB IDs
		"""
		count = 0
		missing_kb_ids: list[str] = []

		for spell_data in spells:
			kb_id = spell_data['name'][6:]  # spell_
			spell = self._spell_repository.get_by_kb_id(kb_id)

			if not spell:
				missing_kb_ids.append(kb_id)
				continue

			inventory = ShopProduct(
				entity_id=spell.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopProductType.SPELL,
				count=spell_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return _SyncItemResult(count=count, missing_kb_ids=missing_kb_ids)

	def _sync_units(
		self,
		units: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int,
		atom_kb_id: str
	) -> _SyncItemResult:
		"""
		Sync unit inventories

		:param units:
			Unit inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param atom_kb_id:
			Shop KB ID for context
		:return:
			Sync result with count and missing KB IDs
		"""
		count = 0
		missing_kb_ids: list[str] = []

		for unit_data in units:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				missing_kb_ids.append(kb_id)
				continue

			inventory = ShopProduct(
				entity_id=unit.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopProductType.UNIT,
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return _SyncItemResult(count=count, missing_kb_ids=missing_kb_ids)

	def _sync_garrison(
		self,
		garrison: list[dict[str, Any]],
		atom_map_id: int,
		profile_id: int,
		atom_kb_id: str
	) -> _SyncItemResult:
		"""
		Sync garrison inventories

		:param garrison:
			Garrison inventory data
		:param atom_map_id:
			Atom map ID
		:param profile_id:
			Profile ID
		:param atom_kb_id:
			Shop KB ID for context
		:return:
			Sync result with count and missing KB IDs
		"""
		count = 0
		missing_kb_ids: list[str] = []

		for unit_data in garrison:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				missing_kb_ids.append(kb_id)
				continue

			inventory = ShopProduct(
				entity_id=unit.id,
				atom_map_id=atom_map_id,
				profile_id=profile_id,
				type=ShopProductType.GARRISON,
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return _SyncItemResult(count=count, missing_kb_ids=missing_kb_ids)

	def _build_corrupted_data(
		self,
		shops: list[str],
		items: list[str],
		units: list[str],
		spells: list[str]
	) -> CorruptedProfileData | None:
		"""
		Build CorruptedProfileData if any missing KB IDs found

		:param shops:
			Missing shop KB IDs
		:param items:
			Missing item KB IDs
		:param spells:
			Missing spell KB IDs
		:param units:
			Missing unit KB IDs
		:return:
			CorruptedProfileData or None if no errors
		"""
		if not any([shops, items, units, spells]):
			return None

		return CorruptedProfileData(
			shops=list(set(shops)) if shops else None,
			items=list(set(items)) if items else None,
			units=list(set(units)) if units else None,
			spells=list(set(spells)) if spells else None
		)
