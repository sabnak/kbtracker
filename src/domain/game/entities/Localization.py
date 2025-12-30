from dataclasses import dataclass

from src.domain.game.entities.LocalizationType import LocalizationType


@dataclass
class Localization:

	id: int
	kb_id: str
	text: str
	type: LocalizationType
