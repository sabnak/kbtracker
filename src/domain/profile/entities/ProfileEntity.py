from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileEntity:
	id: int
	name: str
	game_id: int
	created_at: datetime
