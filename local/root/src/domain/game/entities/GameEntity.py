from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.game.entities.LocStrings import LocStrings


class GameEntity(BaseEntity):

	kb_id: str
	loc: LocStrings | None = None