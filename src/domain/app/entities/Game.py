from dataclasses import dataclass
from datetime import datetime

import pydantic

from src.domain.app.entities.Settings import Settings


class Game(pydantic.BaseModel):
	id: int
	name: str
	path: str
	last_scan_time: datetime | None
