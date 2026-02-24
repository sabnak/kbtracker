import pydantic

from src.domain.app.entities.AppLanguage import AppLanguage


class Settings(pydantic.BaseModel):
	scan_frequency: int = 5
	saves_limit: int = 10
	language: AppLanguage = AppLanguage.RUSSIAN
