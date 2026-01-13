import pydantic


class LocStrings(pydantic.BaseModel):
	name: str | None = None
	hint: str | None = None
	desc: str | None = None
	desc_list: list[str] | None = None
	text: str | None = None
	text_list: list[str] | None = None
	header: str | None = None
