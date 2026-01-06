from dataclasses import dataclass
from datetime import datetime


@dataclass
class Game:
	id: int
	name: str
	path: str
	last_scan_time: datetime | None
