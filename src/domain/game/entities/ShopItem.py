from dataclasses import dataclass

from src.domain.game.entities.Item import Item


@dataclass
class ShopItem:
	item: Item
	count: int
