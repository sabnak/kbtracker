import re
from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.IAtomMapRepository import IAtomMapRepository
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IUnitRepository import IUnitRepository
from src.domain.game.ISpellRepository import ISpellRepository
from src.domain.game.entities.ShopInventoryType import ShopInventoryType


class ShopInventoryService:

	def __init__(
		self,
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository],
		atom_map_repository: IAtomMapRepository = Provide[Container.atom_map_repository],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository],
		item_repository: IItemRepository = Provide[Container.item_repository],
		unit_repository: IUnitRepository = Provide[Container.unit_repository],
		spell_repository: ISpellRepository = Provide[Container.spell_repository]
	):
		self._shop_inventory_repository = shop_inventory_repository
		self._atom_map_repository = atom_map_repository
		self._localization_repository = localization_repository
		self._item_repository = item_repository
		self._unit_repository = unit_repository
		self._spell_repository = spell_repository

	def get_shops_by_location(self, profile_id: int) -> dict[str, list[dict]]:
		"""
		Get all shops grouped by location with enriched inventory data

		:param profile_id:
			Profile ID to filter inventory
		:return:
			Dictionary mapping location names to list of shop data
		"""
		all_inventory = self._shop_inventory_repository.get_by_profile(profile_id, None)

		if not all_inventory:
			return {}

		atom_map_ids = list(set(inv.atom_map_id for inv in all_inventory))
		atom_maps_dict = self._atom_map_repository.get_by_ids(atom_map_ids)

		location_kb_ids = set()
		for atom_map in atom_maps_dict.values():
			location_kb_id = self._extract_location_kb_id(atom_map.kb_id)
			location_kb_ids.add(location_kb_id)

		location_names_dict = {}
		for loc_kb_id in location_kb_ids:
			localization = self._localization_repository.get_by_kb_id(loc_kb_id)
			if localization:
				location_names_dict[loc_kb_id] = localization.text
			else:
				location_names_dict[loc_kb_id] = loc_kb_id

		item_ids = [inv.entity_id for inv in all_inventory if inv.type == ShopInventoryType.ITEM]
		unit_ids = [
			inv.entity_id for inv in all_inventory
			if inv.type in [ShopInventoryType.UNIT, ShopInventoryType.GARRISON]
		]
		spell_ids = [inv.entity_id for inv in all_inventory if inv.type == ShopInventoryType.SPELL]

		items_dict = self._item_repository.get_by_ids(item_ids) if item_ids else {}
		units_dict = self._unit_repository.get_by_ids(unit_ids) if unit_ids else {}
		spells_dict = self._spell_repository.get_by_ids(spell_ids) if spell_ids else {}

		shops_by_atom_map = {}
		for inv in all_inventory:
			atom_map_id = inv.atom_map_id

			if atom_map_id not in shops_by_atom_map:
				shops_by_atom_map[atom_map_id] = {
					"atom_map_id": atom_map_id,
					"items": [],
					"spells": [],
					"units": [],
					"garrison": []
				}

			if inv.type == ShopInventoryType.ITEM:
				item = items_dict.get(inv.entity_id)
				if item:
					shops_by_atom_map[atom_map_id]["items"].append({
						"id": item.id,
						"name": item.name,
						"count": inv.count
					})
			elif inv.type == ShopInventoryType.SPELL:
				spell = spells_dict.get(inv.entity_id)
				if spell and spell.loc and spell.loc.name:
					shops_by_atom_map[atom_map_id]["spells"].append({
						"id": spell.id,
						"name": spell.loc.name,
						"count": inv.count
					})
			elif inv.type == ShopInventoryType.UNIT:
				unit = units_dict.get(inv.entity_id)
				if unit:
					shops_by_atom_map[atom_map_id]["units"].append({
						"id": unit.id,
						"name": unit.name,
						"count": inv.count
					})
			elif inv.type == ShopInventoryType.GARRISON:
				unit = units_dict.get(inv.entity_id)
				if unit:
					shops_by_atom_map[atom_map_id]["garrison"].append({
						"id": unit.id,
						"name": unit.name,
						"count": inv.count
					})

		shops_with_location = []
		for atom_map_id, shop_data in shops_by_atom_map.items():
			atom_map = atom_maps_dict.get(atom_map_id)
			if not atom_map:
				continue

			location_kb_id = self._extract_location_kb_id(atom_map.kb_id)

			shops_with_location.append({
				"shop_id": atom_map.id,
				"shop_loc": atom_map.loc,
				"shop_kb_id": atom_map.kb_id,
				"location_kb_id": location_kb_id,
				"location_name": location_names_dict.get(location_kb_id, location_kb_id),
				"items": shop_data["items"],
				"spells": shop_data["spells"],
				"units": shop_data["units"],
				"garrison": shop_data["garrison"]
			})

		grouped_by_location = {}
		for shop in shops_with_location:
			location_kb_id = shop["location_kb_id"]
			location_name = shop["location_name"]

			if location_kb_id not in grouped_by_location:
				grouped_by_location[location_kb_id] = {
					"name": location_name,
					"shops": []
				}
			grouped_by_location[location_kb_id]["shops"].append(shop)

		for location_kb_id in grouped_by_location:
			grouped_by_location[location_kb_id]["shops"].sort(
				key=lambda s: (
					s["shop_loc"].name if s["shop_loc"] and s["shop_loc"].name
					else s["shop_loc"].hint if s["shop_loc"] and s["shop_loc"].hint
					else s["shop_kb_id"]
				)
			)

		sorted_locations = dict(sorted(grouped_by_location.items(), key=lambda x: x[1]["name"]))

		return sorted_locations

	def _extract_location_kb_id(self, atom_map_kb_id: str) -> str:
		"""
		Extract location kb_id from atom_map kb_id

		:param atom_map_kb_id:
			Atom map kb_id (e.g., 'aralan_1')
		:return:
			Location kb_id (e.g., 'aralan')
		"""
		match = re.match(r'^(.+)_\d+$', atom_map_kb_id)
		if match:
			return match.group(1)
		return atom_map_kb_id
