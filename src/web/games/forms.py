from pydantic import BaseModel, Field
from enum import Enum

from src.web.dependencies.query_params import OptionalInt


class GameCreateForm(BaseModel):
	name: str = Field(..., min_length=1, max_length=255)
	path: str = Field(..., min_length=1, max_length=100)


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
