from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.game.entities.LocStrings import LocStrings


class AtomMap(BaseEntity):

	id: int
	kb_id: str
	loc: LocStrings | None = None
