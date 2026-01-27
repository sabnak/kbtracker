from datetime import datetime

from src.domain.app.entities.Game import Game
from src.domain.base.entities.BaseEntity import BaseEntity
from src.domain.game.entities.MissedShopsData import MissedShopsData


class ProfileEntity(BaseEntity):
	name: str
	created_at: datetime
	hash: str | None = None
	full_name: str | None = None
	save_dir: str | None = None
	last_scan_time: datetime | None = None
	last_save_timestamp: int | None = None
	last_corrupted_data: MissedShopsData | None = None
	is_auto_scan_enabled: bool = True
	game: Game | None = None
