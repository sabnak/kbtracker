from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	db_user: str
	db_password: str
	db_name: str
	db_host: str = "postgres"
	db_port: int = 5432
	game_data_path: str = "/data"

	@property
	def database_url(self) -> str:
		return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

	class Config:
		env_file = ".env"
