import re
import typing

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopInventory import ShopInventory
from src.domain.game.entities.ShopItem import ShopItem
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.entities.ShopSpell import ShopSpell
from src.domain.game.entities.ShopUnit import ShopUnit
from src.domain.game.interfaces.IAtomMapRepository import IAtomMapRepository
from src.domain.game.interfaces.IItemRepository import IItemRepository
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.game.interfaces.ILocationShopFactory import ILocationShopFactory
from src.domain.game.interfaces.ISpellRepository import ISpellRepository
from src.domain.game.interfaces.IUnitRepository import IUnitRepository


class LocationShopFactory(ILocationShopFactory):

	def __init__(
		self,
		products: list[ShopProduct],
		atom_map_repository: IAtomMapRepository = Provide[Container.atom_map_repository],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository],
		item_repository: IItemRepository = Provide[Container.item_repository],
		spell_repository: ISpellRepository = Provide[Container.spell_repository],
		unit_repository: IUnitRepository = Provide[Container.unit_repository]
	):
		self._products = products
		self._atom_map_repository = atom_map_repository
		self._localization_repository = localization_repository
		self._item_repository = item_repository
		self._spell_repository = spell_repository
		self._unit_repository = unit_repository

	def produce(
		self,
		group_by: ShopsGroupBy = ShopsGroupBy.LOCATION
	) -> dict[str, dict[str, list[Shop]]]:
		"""
		Transform products into shops grouped by location

		:return:
			Dictionary mapping location_kb_id to location data with shops
		"""
		if not self._products:
			return {}

		atom_maps_dict = self._fetch_atom_maps()
		location_names_dict = self._fetch_location_names(atom_maps_dict)
		entities = self._fetch_entities()
		shops_by_atom_map = self._group_products_by_shop()
		shops = self._create_shops(shops_by_atom_map, atom_maps_dict, location_names_dict, entities)
		grouped_by_location = self._group_shops_by_location(shops)
		self._sort_shops_within_locations(grouped_by_location)

		return dict(sorted(grouped_by_location.items(), key=lambda x: x[1]["name"]))

	def _fetch_atom_maps(self) -> dict[int, any]:
		"""
		Fetch atom maps for all products

		:return:
			Dictionary mapping atom_map_id to AtomMap entity
		"""
		atom_map_ids = list(set(product.atom_map_id for product in self._products))
		return self._atom_map_repository.get_by_ids(atom_map_ids)

	def _fetch_location_names(self, atom_maps_dict: dict) -> dict[str, str]:
		"""
		Fetch location names for atom maps

		:param atom_maps_dict:
			Dictionary of atom maps
		:return:
			Dictionary mapping location_kb_id to localized name
		"""
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

		return location_names_dict

	def _fetch_entities(self) -> dict:
		"""
		Fetch all entities needed for products

		:return:
			Dictionary with 'items', 'units', 'spells' keys mapping IDs to entities
		"""
		item_ids = [p.entity_id for p in self._products if p.type == ShopProductType.ITEM]
		unit_ids = [
			p.entity_id for p in self._products
			if p.type in [ShopProductType.UNIT, ShopProductType.GARRISON]
		]
		spell_ids = [p.entity_id for p in self._products if p.type == ShopProductType.SPELL]

		return {
			"items": self._item_repository.get_by_ids(item_ids) if item_ids else {},
			"units": self._unit_repository.get_by_ids(unit_ids) if unit_ids else {},
			"spells": self._spell_repository.get_by_ids(spell_ids) if spell_ids else {}
		}

	def _group_products_by_shop(self) -> dict[int, list[ShopProduct]]:
		"""
		Group products by atom_map_id (shop)

		:return:
			Dictionary mapping atom_map_id to list of products
		"""
		shops_by_atom_map = {}
		for product in self._products:
			atom_map_id = product.atom_map_id
			if atom_map_id not in shops_by_atom_map:
				shops_by_atom_map[atom_map_id] = []
			shops_by_atom_map[atom_map_id].append(product)

		return shops_by_atom_map

	def _create_shops(
		self,
		shops_by_atom_map: dict,
		atom_maps_dict: dict,
		location_names_dict: dict,
		entities: dict
	) -> list[Shop]:
		"""
		Create Shop entities from grouped products

		:param shops_by_atom_map:
			Products grouped by atom_map_id
		:param atom_maps_dict:
			Dictionary of atom maps
		:param location_names_dict:
			Dictionary of location names
		:param entities:
			Dictionary of fetched entities
		:return:
			List of Shop entities
		"""
		shops = []
		for atom_map_id, products in shops_by_atom_map.items():
			atom_map = atom_maps_dict.get(atom_map_id)
			if not atom_map:
				continue

			location_kb_id = self._extract_location_kb_id(atom_map.kb_id)
			inventory = self._create_inventory(products, entities)

			shop = Shop(
				shop_id=atom_map.id,
				shop_kb_id=atom_map.kb_id,
				shop_loc=atom_map.loc,
				location_kb_id=location_kb_id,
				location_name=location_names_dict.get(location_kb_id, location_kb_id),
				inventory=inventory
			)
			shops.append(shop)

		return shops

	def _create_inventory(self, products: list[ShopProduct], entities: dict) -> ShopInventory:
		"""
		Create ShopInventory from products

		:param products:
			List of products for a shop
		:param entities:
			Dictionary of fetched entities
		:return:
			ShopInventory entity
		"""
		shop_items = []
		shop_spells = []
		shop_units = []
		garrison_units = []

		for product in products:
			if product.type == ShopProductType.ITEM:
				item = entities["items"].get(product.entity_id)
				if item:
					shop_items.append(ShopItem(item=item, count=product.count))

			elif product.type == ShopProductType.SPELL:
				spell = entities["spells"].get(product.entity_id)
				if spell and spell.loc and spell.loc.name:
					shop_spells.append(ShopSpell(spell=spell, count=product.count))

			elif product.type == ShopProductType.UNIT:
				unit = entities["units"].get(product.entity_id)
				if unit:
					shop_units.append(ShopUnit(unit=unit, count=product.count))

			elif product.type == ShopProductType.GARRISON:
				unit = entities["units"].get(product.entity_id)
				if unit:
					garrison_units.append(ShopUnit(unit=unit, count=product.count))

		return ShopInventory(
			items=shop_items,
			spells=shop_spells,
			units=shop_units,
			garrison=garrison_units
		)

	def _group_shops_by_location(self, shops: list[Shop]) -> dict[str, dict[str, list[Shop]]]:
		"""
		Group shops by location

		:param shops:
			List of Shop entities
		:return:
			Dictionary mapping location_kb_id to location data with shops
		"""
		grouped_by_location = {}
		for shop in shops:
			location_kb_id = shop.location_kb_id
			location_name = shop.location_name

			if location_kb_id not in grouped_by_location:
				grouped_by_location[location_kb_id] = {
					"name": location_name,
					"shops": []
				}
			grouped_by_location[location_kb_id]["shops"].append(shop)

		return grouped_by_location

	def _sort_shops_within_locations(self, grouped_by_location: dict) -> None:
		"""
		Sort shops within each location

		:param grouped_by_location:
			Dictionary of grouped shops (modified in place)
		"""
		for location_kb_id in grouped_by_location:
			grouped_by_location[location_kb_id]["shops"].sort(
				key=lambda s: (
					s.shop_loc.name if s.shop_loc and s.shop_loc.name
					else s.shop_loc.hint if s.shop_loc and s.shop_loc.hint
					else s.shop_kb_id
				)
			)

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
