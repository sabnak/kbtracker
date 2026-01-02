from dataclasses import dataclass

from src.domain.game.entities.UnitClass import UnitClass


@dataclass
class Unit:

	id: int
	kb_id: str
	name: str
	unit_class: UnitClass
	main: dict[str, any]
	params: dict[str, any]
	features: dict[str, any] = None
	actions: dict[str, any] = None
