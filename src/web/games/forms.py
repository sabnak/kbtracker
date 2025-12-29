from pydantic import BaseModel, Field
from enum import Enum


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
