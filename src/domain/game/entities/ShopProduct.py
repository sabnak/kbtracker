import pydantic
from pydantic import ConfigDict

from src.domain.game.entities.ShopProductType import ShopProductType


class ShopProduct(pydantic.BaseModel):
	model_config = ConfigDict(from_attributes=True)

	entity_id: int
	atom_map_id: int
	profile_id: int
	type: ShopProductType
	count: int
