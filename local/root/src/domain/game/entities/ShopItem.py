from dataclasses import dataclass

import pydantic

from src.domain.game.entities.Item import Item


class ShopItem(pydantic.BaseModel):
	item: Item
	count: int
