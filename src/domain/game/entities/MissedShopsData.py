from pydantic import BaseModel


class MissedShopsData(BaseModel):
	items: list[str] | None = None
	shops: list[str] | None = None
	units: list[str] | None = None
	spells: list[str] | None = None
