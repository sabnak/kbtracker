from dataclasses import dataclass
from src.domain.game.entities.Propbit import Propbit


@dataclass
class Item:

	id: int
	game_id: int
	item_set_id: int | None
	kb_id: str
	name: str
	price: int
	hint: str | None
	propbits: list[Propbit] | None
	level: int = 1
