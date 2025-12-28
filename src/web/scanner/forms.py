from pydantic import BaseModel
from enum import Enum


class LanguageEnum(str, Enum):
	RUSSIAN = "ru"
	ENGLISH = "eng"
	GERMAN = "ger"
	POLISH = "pol"


class ScanForm(BaseModel):
	language: LanguageEnum
