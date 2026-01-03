from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProfileEntity:
	id: int
	name: str
	created_at: datetime
	hash: str | None = None
	full_name: str | None = None
	save_dir: str | None = None
