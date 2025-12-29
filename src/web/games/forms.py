from pydantic import BaseModel, Field


class GameCreateForm(BaseModel):
	name: str = Field(..., min_length=1, max_length=255)
	path: str = Field(..., min_length=1, max_length=100)
