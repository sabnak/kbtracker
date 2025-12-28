from pydantic import BaseModel, Field


class ProfileCreateForm(BaseModel):
	name: str = Field(..., min_length=1, max_length=255)
	game_path: str = Field(..., min_length=1, max_length=100)
