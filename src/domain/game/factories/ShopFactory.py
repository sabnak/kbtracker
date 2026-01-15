from typing import Any

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.Actor import Actor
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.entities.Shop import Shop
from src.domain.game.entities.ShopInventory import ShopInventory
from src.domain.game.entities.ShopItem import ShopItem
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.entities.ShopSpell import ShopSpell
from src.domain.game.entities.ShopType import ShopType
from src.domain.game.entities.ShopUnit import ShopUnit
from src.domain.game.interfaces.IEntityRepository import IEntityRepository
from src.domain.game.interfaces.IItemRepository import IItemRepository
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.game.interfaces.IShopFactory import IShopFactory
from src.domain.game.interfaces.ISpellRepository import ISpellRepository
from src.domain.game.interfaces.IUnitRepository import IUnitRepository


class ShopFactory(IShopFactory):

	def __init__(
		self,
		products: list[ShopProduct],
		atom_map_repository: IEntityRepository[AtomMap] = Provide[Container.atom_map_repository],
		actor_repository: IEntityRepository[Actor] = Provide[Container.actor_repository],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository],
		item_repository: IItemRepository = Provide[Container.item_repository],
		spell_repository: ISpellRepository = Provide[Container.spell_repository],
		unit_repository: IUnitRepository = Provide[Container.unit_repository]
	):
		self._products = products
		self._atom_map_repository = atom_map_repository
		self._actor_repository = actor_repository
		self._localization_repository = localization_repository
		self._item_repository = item_repository
		self._spell_repository = spell_repository
		self._unit_repository = unit_repository

	def produce(self) -> list[Shop]:
		"""
		Transform products into a flat list of shops

		:return:
			List of Shop entities
		"""
		if not self._products:
			return []

		atom_map_ids = []
		actor_ids = []
		location_kb_ids = []
		for product in self._products:
			if product.shop_type == ShopType.ATOM:
				atom_map_ids.append(product.shop_id)
			elif product.shop_type == ShopType.ACTOR:
				actor_ids.append(product.shop_id)
			location_kb_ids.append(product.location)
		atom_maps = self._atom_map_repository.get_by_ids(set(atom_map_ids))
		actors = self._actor_repository.get_by_ids(set(actor_ids))
		location_names_dict = self._fetch_location_names(location_kb_ids)

		products = self._fetch_products()
		shops_group = self._group_products_by_shop()
		shops = self._create_shops(shops_group, atom_maps, actors, location_names_dict, products)

		return shops

	def _fetch_atom_maps(self) -> dict[int, Any]:
		"""
		Fetch atom maps for all products

		:return:
			Dictionary mapping atom_map_id to AtomMap entity
		"""
		atom_map_ids = list(set(product.atom_map_id for product in self._products))
		return self._atom_map_repository.get_by_ids(atom_map_ids)

	def _fetch_location_names(self, location_kb_ids: list[str]) -> dict[str, str]:
		location_names_dict = {}
		for loc_kb_id in location_kb_ids:
			localization = self._localization_repository.get_by_kb_id(loc_kb_id)
			if localization:
				location_names_dict[loc_kb_id] = localization.text
			else:
				location_names_dict[loc_kb_id] = loc_kb_id

		return location_names_dict

	def _fetch_products(self) -> dict:
		item_ids = [p.product_id for p in self._products if p.product_type == ShopProductType.ITEM]
		unit_ids = [
			p.product_id for p in self._products
			if p.product_type in [ShopProductType.UNIT, ShopProductType.GARRISON]
		]
		spell_ids = [p.product_id for p in self._products if p.product_type == ShopProductType.SPELL]

		return {
			"items": self._item_repository.get_by_ids(item_ids) if item_ids else {},
			"units": self._unit_repository.get_by_ids(unit_ids) if unit_ids else {},
			"spells": self._spell_repository.get_by_ids(spell_ids) if spell_ids else {}
		}

	def _group_products_by_shop(self) -> dict[(int, ShopType), list[ShopProduct]]:
		"""
		Group products by atom_map_id (shop)

		:return:
			Dictionary mapping atom_map_id to list of products
		"""
		shops_group = {}
		for product in self._products:
			shop_id = (product.shop_id, product.shop_type)
			if shop_id not in shops_group:
				shops_group[shop_id] = []
			shops_group[shop_id].append(product)

		return shops_group

	def _create_shops(
		self,
		shops_group: dict,
		atom_maps: dict,
		actors: dict,
		location_names_dict: dict,
		entities: dict
	) -> list[Shop]:
		shops = []
		for (shop_id, shop_type), products in shops_group.items():
			if shop_type == ShopType.ATOM:
				s = atom_maps[shop_id]
			else:
				s = actors[shop_id]

			inventory = self._create_inventory(products, entities)
			location_kb_id = products[0].location

			shop = Shop(
				shop_id=shop_id,
				shop_type=shop_type,
				shop_kb_id=s.kb_id,
				shop_loc=s.loc,
				location_kb_id=location_kb_id,
				location_name=location_names_dict.get(location_kb_id, location_kb_id),
				inventory=inventory
			)
			shops.append(shop)

		return shops

	@staticmethod
	def _create_inventory(products: list[ShopProduct], entities: dict) -> ShopInventory:
		shop_items = []
		shop_spells = []
		shop_units = []
		garrison_units = []

		for product in products:
			if product.product_type == ShopProductType.ITEM:
				item = entities["items"].get(product.product_id)
				if item:
					shop_items.append(ShopItem(item=item, count=product.count))

			elif product.product_type == ShopProductType.SPELL:
				spell = entities["spells"].get(product.product_id)
				if spell and spell.loc and spell.loc.name:
					shop_spells.append(ShopSpell(spell=spell, count=product.count))

			elif product.product_type == ShopProductType.UNIT:
				unit = entities["units"].get(product.product_id)
				if unit:
					shop_units.append(ShopUnit(unit=unit, count=product.count))

			elif product.product_type == ShopProductType.GARRISON:
				unit = entities["units"].get(product.product_id)
				if unit:
					garrison_units.append(ShopUnit(unit=unit, count=product.count))

		return ShopInventory(
			items=shop_items,
			spells=shop_spells,
			units=shop_units,
			garrison=garrison_units
		)
