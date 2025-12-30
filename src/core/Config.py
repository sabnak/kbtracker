from pydantic_settings import BaseSettings


class Config(BaseSettings):

	game_data_path: str = "/data"

	localization_files: list[str] = [
		"items",
		"units",
		"units_features",
		"units_specials"
	]
