from dataclasses import dataclass


@dataclass
class Localization:

	id: int
	kb_id: str
	text: str
	source: str | None
