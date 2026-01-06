from pydantic import BaseModel, Field


class SettingsForm(BaseModel):
	sync_frequency: int = Field(..., gt=0, le=60)
	saves_limit: int = Field(..., gt=0, le=100)
