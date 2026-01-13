import os.path
import re

from pydantic_settings import BaseSettings


class LocalizationConfig(BaseSettings):
	file: str
	tag: str | None = None
	pattern: re.Pattern | None = None


class GameConfig(BaseSettings):

	name: str
	core_session_path: str
	campaigns: list['GameConfig'] | None = None
	save_path_pattern: str | None = None


class Config(BaseSettings):

	game_data_path: str = "/data"
	game_save_path: str = "/saves"

	tmp_dir: str = "/tmp"

	data_archive_patterns: list[str] = [
		"{game_path}/data/data.kfs",
		"{game_path}/sessions/*/ses*.kfs"
	]

	loc_archive_patterns: list[str] = [
		"{game_path}/sessions/*/loc_ses*.kfs"
	]

	localization_config: list[LocalizationConfig] = [
		LocalizationConfig(file="items", tag="items"),
		LocalizationConfig(file="units", tag="units"),
		LocalizationConfig(file="units_features", tag="units_features"),
		LocalizationConfig(file="units_specials", tag="units_specials"),
		LocalizationConfig(file="spells", tag="spells"),
		LocalizationConfig(file="atoms_info", tag="atoms_info"),
		LocalizationConfig(file="map", tag="maps"),
	]
	supported_games: list[GameConfig] = [
		GameConfig(
			name="Легенда / The Legend",
			core_session_path="data"
		),
		GameConfig(
			name="Принцесса в доспехах / Armored Princess",
			core_session_path="addon"
		),
		GameConfig(
			name="Перекрёстки миров / Crossworlds",
			core_session_path="addon",
			save_path_pattern=os.path.join("Kings Bounty Crossworlds", "$save", "{campaign_name}_*.sav"),
			campaigns=[
				GameConfig(
					name="Принцесса в доспехах / Armored Princess",
					core_session_path="addon"
				),
				GameConfig(
					name="Чемпион арены / Champion of the Arena",
					core_session_path="champion"
				),
				GameConfig(
					name="Защитник короны / Defender of the Crown",
					core_session_path="defender"
				),
				GameConfig(
					name="Поход орков / Orcs on the March",
					core_session_path="orcs"
				),
				GameConfig(
					name="Красные пески / Red Sands",
					core_session_path="red_sands"
				)
			]
		),
		GameConfig(
			name="Воин Севера / Warriors of the North",
			core_session_path="addon",
			campaigns=[
				GameConfig(
					name="Лёд и пламя / Ice and Fire",
					core_session_path="ice_and_fire"
				)
			]
		),
		GameConfig(
			name="Тёмная сторона / Dark side",
			core_session_path="darkside",
			save_path_pattern=os.path.join("Kings Bounty The Dark Side", "$save", "base", "darkside", "*")
		)
	]
