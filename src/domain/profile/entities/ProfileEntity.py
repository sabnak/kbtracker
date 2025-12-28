from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileEntity:
	id: int
	name: str
	game_path: str
	created_at: datetime
