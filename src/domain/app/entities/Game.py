from datetime import datetime

import pydantic


class Game(pydantic.BaseModel):
	id: int
	name: str
	path: str
	last_scan_time: datetime | None
	sessions: list[str]
	saves_pattern: str
