from pydantic_settings import BaseSettings


class Config(BaseSettings):

	game_data_path: str = "/data"

	localization_files: dict[str, str] = {
		"items": "items",
		"units": "units",
		"units_features": "units_features",
		"units_specials": "units_specials"
	}
