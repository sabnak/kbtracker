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


class SpellFilterForm(BaseModel):
	profile_id: OptionalInt = None
	school: str = ""
	profit: OptionalInt = None
	sort_by: str = "name"
	sort_order: str = "asc"

	@field_validator("sort_by")
	@classmethod
	def validate_sort_by(cls, v: str) -> str:
		"""
		Validate sort_by field

		:param v:
			Sort by value
		:return:
			Validated sort field
		"""
		allowed = ["name", "school", "mana", "crystal", "profit"]
		return v if v in allowed else "name"

	@field_validator("sort_order")
	@classmethod
	def validate_sort_order(cls, v: str) -> str:
		"""
		Validate sort_order field

		:param v:
			Sort order value
		:return:
			Validated sort order
		"""
		return v.lower() if v.lower() in ["asc", "desc"] else "asc"


class UnitFilterForm(BaseModel):
	profile_id: OptionalInt = None
	min_cost: OptionalInt = None
	max_cost: OptionalInt = None

	# Numeric attribute filters (min values)
	min_attack: OptionalInt = None
	min_krit: OptionalInt = None
	min_hitpoint: OptionalInt = None
	min_defense: OptionalInt = None
	min_speed: OptionalInt = None
	min_initiative: OptionalInt = None

	# Resistance filters (min values)
	min_resistance_fire: OptionalInt = None
	min_resistance_magic: OptionalInt = None
	min_resistance_poison: OptionalInt = None
	min_resistance_glacial: OptionalInt = None
	min_resistance_physical: OptionalInt = None
	min_resistance_astral: OptionalInt = None

	# Level filter (exact match)
	level: OptionalInt = None
