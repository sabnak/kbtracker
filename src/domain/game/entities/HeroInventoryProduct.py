from pydantic import BaseModel, ConfigDict

from src.domain.game.entities.InventoryEntityType import InventoryEntityType


class HeroInventoryProduct(BaseModel):

	model_config = ConfigDict(from_attributes=True)

	product_id: int
	product_type: InventoryEntityType
	count: int
	profile_id: int
