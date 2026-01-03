import re

from pydantic_settings import BaseSettings


class LocalizationConfig(BaseSettings):
	file: str
	tag: str | None = None
	pattern: re.Pattern | None = None


class Config(BaseSettings):

	game_data_path: str = "/data"
	game_save_path: str = "/save"

	tmp_dir: str = "/tmp"

	data_archive_patterns: list[str] = [
		"{game_path}/data/data.kfs",
		"{game_path}/sessions/*/ses*.kfs"
	]

	loc_archive_patterns: list[str] = [
		"{game_path}/sessions/*/loc_ses*.kfs"
	]

	localization_config: ['LocalizationConfig'] = [
		LocalizationConfig(file="items", tag="items"),
		LocalizationConfig(file="units", tag="units"),
		LocalizationConfig(file="units_features", tag="units_features"),
		LocalizationConfig(file="units_specials", tag="units_specials"),
		LocalizationConfig(file="spells", tag="spells"),
	]

