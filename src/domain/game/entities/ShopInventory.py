from dataclasses import dataclass

from src.domain.game.entities.ShopItem import ShopItem
from src.domain.game.entities.ShopSpell import ShopSpell
from src.domain.game.entities.ShopUnit import ShopUnit


@dataclass
class ShopInventory:
	items: list[ShopItem]
	spells: list[ShopSpell]
	units: list[ShopUnit]
	garrison: list[ShopUnit]
