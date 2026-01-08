from dataclasses import dataclass

from src.domain.game.entities.Spell import Spell


@dataclass
class ShopSpell:
	spell: Spell
	count: int
