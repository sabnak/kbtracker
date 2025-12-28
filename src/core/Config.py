from pydantic_settings import BaseSettings


class Config(BaseSettings):
	game_data_path: str = "/data"
