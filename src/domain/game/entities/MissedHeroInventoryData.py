from pydantic import BaseModel


class MissedHeroInventoryData(BaseModel):
	items: list[str] | None = None
