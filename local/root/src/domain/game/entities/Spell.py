from typing import Any

from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.SpellSchool import SpellSchool


class Spell(BaseEntity):

	kb_id: str
	profit: int
	price: int
	school: SpellSchool
	data: dict[str, Any]
	hide: int = 0
	mana_cost: list[int] | None = None
	crystal_cost: list[int] | None = None
	loc: LocStrings | None = None
