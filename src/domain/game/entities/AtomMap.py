from dataclasses import dataclass

from src.domain.game.entities.LocStrings import LocStrings


@dataclass
class AtomMap:

	id: int
	kb_id: str
	loc: LocStrings | None = None
