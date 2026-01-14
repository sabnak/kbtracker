import os.path
import re

from pydantic_settings import BaseSettings

from src.core.GameConfig import GameConfig, GameCampaignConfig


class LocalizationConfig(BaseSettings):
	file: str
	tag: str | None = None
	pattern: re.Pattern | None = None


class Config(BaseSettings):

	game_data_path: str = "/data"
	game_save_path: str = "/saves"

	tmp_dir: str = "/tmp"

	data_archive_path: str = "{game_path}/data/data.kfs"
	session_archives_pattern: str = "{game_path}/sessions/{session}/*.kfs"

	localization_config: list[LocalizationConfig] = [
		LocalizationConfig(file="items", tag="items"),
		LocalizationConfig(file="units", tag="units"),
		LocalizationConfig(file="orcs_rage", tag="units"),
		LocalizationConfig(file="units_features", tag="units_features"),
		LocalizationConfig(file="units_specials", tag="units_specials"),
		LocalizationConfig(file="spells", tag="spells"),
		LocalizationConfig(file="atoms_info", tag="atoms_info"),
		LocalizationConfig(file="map", tag="maps"),
	]
	supported_games: list[GameConfig] = [
		GameConfig(
			name="Легенда / The Legend",
			session="base",
			saves_pattern=os.path.join("Kings Bounty Legend", "$save", "*.sav"),
		),
		GameConfig(
			name="Принцесса в доспехах / Armored Princess",
			session="addon",
			saves_pattern=os.path.join("Kings Bounty Armored Princess", "$save", "*.sav"),
		),
		GameConfig(
			name="Перекрёстки миров / Crossworlds",
			session="addon",
			saves_pattern=os.path.join("Kings Bounty Crossworlds", "$save", "{campaign_session}_*.sav"),
			campaigns=[
				GameCampaignConfig(
					name="Принцесса в доспехах / Armored Princess",
					session="addon"
				),
				GameCampaignConfig(
					name="Чемпион арены / Champion of the Arena",
					session="champion"
				),
				GameCampaignConfig(
					name="Защитник короны / Defender of the Crown",
					session="defender"
				),
				GameCampaignConfig(
					name="Поход орков / Orcs on the March",
					session="orcs"
				),
				GameCampaignConfig(
					name="Красные пески / Red Sands",
					session="red_sands"
				)
			]
		),
		GameConfig(
			name="Воин Севера / Warriors of the North",
			session="addon",
			saves_pattern=os.path.join("Kings Bounty Warriors of the North", "$save", "{campaign_session}_*.sav"),
			campaigns=[
				GameCampaignConfig(
					name="Лёд и пламя / Ice and Fire",
					session="ice_and_fire"
				)
			]
		),
		GameConfig(
			name="Тёмная сторона / Dark side",
			session="darkside",
			saves_pattern=os.path.join("Kings Bounty The Dark Side", "$save", "base", "darkside", "*")
		)
	]
