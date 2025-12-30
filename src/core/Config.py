import re

from pydantic_settings import BaseSettings


class LocalizationConfig(BaseSettings):
	file: str
	tag: str | None = None
	pattern: re.Pattern | None = None


class Config(BaseSettings):

	game_data_path: str = "/data"

	localization_config: ['LocalizationConfig'] = [
		LocalizationConfig(file="items", tag="items"),
		LocalizationConfig(file="units", tag="units"),
		LocalizationConfig(file="units_features", tag="units_features"),
		LocalizationConfig(file="units_specials", tag="units_specials"),
	]

