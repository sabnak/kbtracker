from dataclasses import dataclass


@dataclass
class ItemSet:
	id: int
	game_id: int
	kb_id: str
	name: str
	hint: str | None
