from dataclasses import dataclass

from src.domain.game.entities.Unit import Unit


@dataclass
class ShopUnit:
	unit: Unit
	count: int
