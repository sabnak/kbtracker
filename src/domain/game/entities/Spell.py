from dataclasses import dataclass
from typing import Any

from src.domain.game.entities.LocEntity import LocEntity
from src.domain.game.entities.SpellSchool import SpellSchool


@dataclass
class Spell:

	id: int
	kb_id: str
	profit: int
	price: int
	school: SpellSchool
	data: dict[str, Any]
	mana_cost: list[int] | None = None
	crystal_cost: list[int] | None = None
	loc: LocEntity | None = None
