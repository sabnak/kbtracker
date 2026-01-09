from dataclasses import dataclass
from typing import Any

import pydantic

from src.domain.game.entities.ShopItem import ShopItem
from src.domain.game.entities.ShopSpell import ShopSpell
from src.domain.game.entities.ShopUnit import ShopUnit


class ShopInventory(pydantic.BaseModel):
	items: list[ShopItem]
	spells: list[ShopSpell]
	units: list[ShopUnit]
	garrison: list[ShopUnit]

	_items_index: dict[int, ShopItem] = None
	_spells_index: dict[int, ShopSpell] = None
	_units_index: dict[int, ShopUnit] = None
	_garrison_index: dict[int, ShopUnit] = None

	def model_post_init(self, _: Any):
		self._items_index = {s.item.id: s for s in self.items}
		self._spells_index = {s.spell.id: s for s in self.spells}
		self._units_index = {s.unit.id: s for s in self.units}
		self._garrison_index = {s.unit.id: s for s in self.garrison}

	def get_item(self, item_id: int) -> ShopItem:
		return self._items_index[item_id]

	def get_spell(self, item_id: int) -> ShopSpell:
		return self._spells_index[item_id]

	def get_unit(self, item_id: int) -> ShopUnit:
		return self._units_index[item_id]

	def get_garrison_unit(self, item_id: int) -> ShopUnit:
		return self._garrison_index[item_id]
