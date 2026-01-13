import pydantic

from src.domain.game.entities.Unit import Unit


class ShopUnit(pydantic.BaseModel):
	unit: Unit
	count: int
