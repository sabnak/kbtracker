from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileEntity:
	id: int
	name: str
	created_at: datetime
