from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	game_data_path: str = "/data"
