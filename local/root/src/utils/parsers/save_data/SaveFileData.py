import typing

import pydantic


class GameObjectData(pydantic.BaseModel):
	kb_id: str
	quantity: int


class HeroInventory(pydantic.BaseModel):
	items: list['GameObjectData']


class SaveFileData(pydantic.BaseModel):
	shops: list[dict[str, typing.Any]]
	hero_inventory: HeroInventory | None = None
