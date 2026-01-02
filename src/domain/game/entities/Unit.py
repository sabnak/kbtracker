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
	cost: int | None = None
	krit: int | None = None
	race: str | None = None
	level: int | None = None
	speed: int | None = None
	attack: int | None = None
	defense: int | None = None
	hitback: int | None = None
	hitpoint: int | None = None
	movetype: int | None = None
	defenseup: int | None = None
	initiative: int | None = None
	leadership: int | None = None
	resistance: dict[str, int] | None = None
	features: dict[str, dict[str, str]] | None = None
	attacks: dict[str, dict[str, any]] | None = None
