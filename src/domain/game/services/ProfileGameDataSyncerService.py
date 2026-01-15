import typing
from dataclasses import dataclass
from typing import Any

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.game.entities.Actor import Actor
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.entities.ShopType import ShopType
from src.domain.game.interfaces.IEntityRepository import IEntityRepository
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
		atom_map_repository: IEntityRepository[AtomMap] = Provide[Container.atom_map_repository],
		actor_repository: IEntityRepository[Actor] = Provide[Container.actor_repository],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository]
	):
		self._item_repository = item_repository
		self._spell_repository = spell_repository
		self._unit_repository = unit_repository
		self._atom_map_repository = atom_map_repository
		self._actor_repository = actor_repository
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
		missing_data = {"items": [], "spells": [], "units": [], "garrison": [], "shops": []}

		for shop_data in data:
			params: dict[str, int | None | ShopType | str] = dict(
				shop_id=None,
				profile_id=profile_id,
				location=shop_data.get('location')
			)
			if shop_data['itext']:
				kb_id = shop_data['itext']
				params['shop_id'] = self._atom_map_repository.get_by_kb_id(kb_id).id
				params['shop_type'] = ShopType.ATOM
			else:
				kb_id = shop_data['actor']
				params['shop_id'] = self._actor_repository.get_by_kb_id(kb_id).id
				params['shop_type'] = ShopType.ACTOR

			if not params['shop_id']:
				missing_data["shops"].append(kb_id)
				continue

			inventory = shop_data['inventory']

			for (key, kb_id_fn, product_type, repository) in (
				("items", None, ShopProductType.ITEM, self._item_repository),
				("spells", lambda n: n[6:], ShopProductType.SPELL, self._spell_repository),    # spell_
				("units", None, ShopProductType.UNIT, self._unit_repository),
				("garrison", None, ShopProductType.GARRISON, self._unit_repository),
			):
				result = self._sync(
					inventory[key],
					kb_id_fn=kb_id_fn,
					product_type=product_type,
					repository=repository,
					**params
				)
				counts[key] += result.count
				missing_data[key].extend(result.missing_kb_ids)

		corrupted_data = self._build_corrupted_data(
			shops=missing_data["shops"],
			items=missing_data["items"],
			spells=missing_data["spells"],
			units=missing_data["units"]
		)

		return ProfileSyncResult(
			items=counts["items"],
			spells=counts["spells"],
			units=counts["units"],
			garrison=counts["garrison"],
			corrupted_data=corrupted_data
		)

	def _sync(
		self,
		raw_datas: list[dict[str, Any]],
		shop_id: int,
		shop_type: ShopType,
		profile_id: int,
		location: str | None,
		kb_id_fn: typing.Callable[[str], str],
		product_type: ShopProductType,
		repository
	) -> _SyncItemResult:
		count = 0
		missing_kb_ids: list[str] = []

		for raw_data in raw_datas:
			kb_id = kb_id_fn(raw_data['name']) if kb_id_fn else raw_data['name']
			product: BaseEntity = repository.get_by_kb_id(kb_id)

			if not product:
				missing_kb_ids.append(kb_id)
				continue

			inventory = ShopProduct(
				product_id=product.id,
				shop_id=shop_id,
				shop_type=shop_type,
				profile_id=profile_id,
				product_type=product_type,
				count=raw_data['quantity'],
				location=location
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return _SyncItemResult(count=count, missing_kb_ids=missing_kb_ids)

	@staticmethod
	def _build_corrupted_data(
		shops: list[str],
		items: list[str],
		units: list[str],
		spells: list[str]
	) -> CorruptedProfileData | None:
		if not any([shops, items, units, spells]):
			return None

		return CorruptedProfileData(
			shops=list(set(shops)) if shops else None,
			items=list(set(items)) if items else None,
			units=list(set(units)) if units else None,
			spells=list(set(spells)) if spells else None
		)
