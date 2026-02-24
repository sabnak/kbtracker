from datetime import datetime

from src.domain.base.entities.BaseEntity import BaseEntity


class Game(BaseEntity):
	name: str
	path: str
	last_scan_time: datetime | None
	sessions: list[str]
	saves_pattern: str
