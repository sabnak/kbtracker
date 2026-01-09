from dataclasses import dataclass

import pydantic

from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.ShopInventory import ShopInventory


class Shop(pydantic.BaseModel):
	shop_id: int
	shop_kb_id: str
	shop_loc: LocStrings | None
	location_kb_id: str
	location_name: str
	inventory: ShopInventory
