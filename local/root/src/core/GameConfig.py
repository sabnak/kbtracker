from pydantic_settings import BaseSettings


class GameCampaignConfig(BaseSettings):
	name: str
	session: str


class GameConfig(GameCampaignConfig):

	saves_pattern: str
	campaigns: list['GameCampaignConfig'] | None = None
