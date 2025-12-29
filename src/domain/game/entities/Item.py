from dataclasses import dataclass


@dataclass
class Item:
	id: int
	game_id: int
	item_set_id: int | None
	kb_id: str
	name: str
	price: int
	hint: str | None
	propbits: list[str] | None
	level: int = 1
