from typing import Any

from src.domain.game.entities.BaseEntity import BaseEntity
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.entities.UnitMovetype import UnitMovetype


class Unit(BaseEntity):

	kb_id: str
	name: str
	unit_class: UnitClass
	main: dict[str, Any]
	params: dict[str, Any]
	cost: int | None = None
	krit: int | None = None
	race: str | None = None
	level: int | None = None
	speed: int | None = None
	attack: int | None = None
	defense: int | None = None
	hitback: int | None = None
	hitpoint: int | None = None
	movetype: UnitMovetype | None = None
	defenseup: int | None = None
	initiative: int | None = None
	leadership: int | None = None
	resistance: dict[str, float] | None = None
	features: dict[str, dict[str, str]] | None = None
	attacks: dict[str, dict[str, Any]] | None = None
