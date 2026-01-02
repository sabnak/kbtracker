from dataclasses import dataclass

from src.domain.game.entities.UnitClass import UnitClass


@dataclass
class Unit:

	id: int
	kb_id: str
	name: str
	unit_class: UnitClass
	params: dict[str, any]
