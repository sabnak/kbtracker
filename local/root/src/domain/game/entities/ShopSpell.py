import pydantic

from src.domain.game.entities.Spell import Spell


class ShopSpell(pydantic.BaseModel):
	spell: Spell
	count: int
