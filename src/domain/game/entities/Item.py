from src.domain.game.entities.BaseEntity import BaseEntity
from src.domain.game.entities.Propbit import Propbit


class Item(BaseEntity):

	item_set_id: int | None
	kb_id: str
	name: str
	price: int
	hint: str | None
	propbits: list[Propbit] | None
	tiers: list[str] | None
	level: int = 1
