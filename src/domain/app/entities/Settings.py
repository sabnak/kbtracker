import pydantic


class Settings(pydantic.BaseModel):

	scan_frequency: int = 5
	saves_limit: int = 10
