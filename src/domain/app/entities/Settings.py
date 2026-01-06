import pydantic


class Settings(pydantic.BaseModel):

	sync_frequency: int = 5
	saves_limit: int = 10
