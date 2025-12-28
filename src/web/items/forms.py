from pydantic import BaseModel, Field


class ItemTrackForm(BaseModel):
	item_id: int = Field(..., gt=0)
	object_id: int = Field(..., gt=0)
	count: int = Field(default=1, gt=0)
