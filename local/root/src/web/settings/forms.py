from pydantic import BaseModel, Field, field_validator

from src.domain.app.entities.AppLanguage import AppLanguage


class SettingsForm(BaseModel):
	scan_frequency: int = Field(..., gt=0, le=60)
	saves_limit: int = Field(..., gt=0, le=100)
	language: str

	@field_validator('language')
	@classmethod
	def validate_language(cls, v: str) -> str:
		try:
			AppLanguage[v]
			return v
		except KeyError:
			raise ValueError(f"Invalid language: must be one of {', '.join([lang.name for lang in AppLanguage])}")
