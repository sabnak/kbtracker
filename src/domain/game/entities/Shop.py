from dataclasses import dataclass


@dataclass
class Shop:
	id: int
	kb_id: str
	location_id: int
	name: str
	hint: str | None
	msg: str | None
