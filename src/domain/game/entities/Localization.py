from dataclasses import dataclass


@dataclass
class Localization:

	id: int
	game_id: int
	kb_id: str
	text: str
	source: str | None
	tag: str | None = None
