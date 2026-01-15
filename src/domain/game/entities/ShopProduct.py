import pydantic
from pydantic import ConfigDict

from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.entities.ShopType import ShopType


class ShopProduct(pydantic.BaseModel):
	model_config = ConfigDict(from_attributes=True)

	product_id: int
	product_type: ShopProductType
	count: int
	shop_id: int
	shop_type: ShopType
	location: str | None = None
	profile_id: int
