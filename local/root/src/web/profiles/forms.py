from pydantic import BaseModel, Field


class ProfileCreateForm(BaseModel):
	name: str = Field(..., min_length=1, max_length=255)
	game_id: int = Field(..., gt=0)


class ItemTrackForm(BaseModel):
	item_id: int = Field(..., gt=0)
	shop_id: int = Field(..., gt=0)
	count: int = Field(default=1, gt=0)
