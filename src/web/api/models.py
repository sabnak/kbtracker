from pydantic import BaseModel, Field


class AddShopToItemRequest(BaseModel):
	shop_id: int = Field(..., gt=0)
	count: int = Field(default=1, ge=0, le=99999)


class UpdateShopCountRequest(BaseModel):
	count: int = Field(..., ge=0, le=99999)
