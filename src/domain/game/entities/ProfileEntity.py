from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from src.domain.game.entities.CorruptedProfileData import CorruptedProfileData

if TYPE_CHECKING:
	from src.domain.app.entities.Game import Game


@dataclass
class ProfileEntity:
	id: int
	name: str
	created_at: datetime
	hash: str | None = None
	full_name: str | None = None
	save_dir: str | None = None
	last_scan_time: datetime | None = None
	last_save_timestamp: int | None = None
	last_corrupted_data: CorruptedProfileData | None = None
	is_auto_scan_enabled: bool = True
	game: 'Game | None' = None
