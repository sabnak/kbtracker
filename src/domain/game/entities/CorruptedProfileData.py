from pydantic import BaseModel


class CorruptedProfileData(BaseModel):
	items: list[str] | None = None
	shops: list[str] | None = None
	units: list[str] | None = None
	garrison: list[str] | None = None
