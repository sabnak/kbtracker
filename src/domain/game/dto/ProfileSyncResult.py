from pydantic import BaseModel

from src.domain.game.entities.CorruptedProfileData import CorruptedProfileData


class ProfileSyncResult(BaseModel):
	items: int
	spells: int
	units: int
	garrison: int
	corrupted_data: CorruptedProfileData | None = None
