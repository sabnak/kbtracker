from pydantic import BaseModel, Field, field_validator
from enum import Enum

from src.web.dependencies.query_params import OptionalInt


class GameCreateForm(BaseModel):
	name: str = Field(..., min_length=1, max_length=255)
	path: str = Field(..., min_length=1, max_length=100)
	game_type: str = Field(..., min_length=1)
	campaign_name: str | None = None
	custom_campaign_session: str | None = None

	@field_validator('custom_campaign_session')
	@classmethod
	def validate_custom_session(cls, v: str | None) -> str | None:
		"""
		Validate custom campaign session

		:param v:
			Custom campaign session value
		:return:
			Cleaned value or None
		"""
		if v and not v.strip():
			return None
		return v


class LanguageEnum(str, Enum):
	RUSSIAN = "rus"
	ENGLISH = "eng"
	GERMAN = "ger"
	POLISH = "pol"


class ScanForm(BaseModel):
	language: LanguageEnum


class UnitFilterForm(BaseModel):
	profile_id: OptionalInt = None
	min_cost: OptionalInt = None
	max_cost: OptionalInt = None
