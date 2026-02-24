import os

from dependency_injector.wiring import inject, Provide

from src.core.Config import Config
from src.core.Container import Container
from src.core.GameConfig import GameConfig
from src.domain.app.interfaces.IGameConfigService import IGameConfigService


class GameConfigService(IGameConfigService):

	@inject
	def __init__(self, config: Config = Provide[Container.config]):
		"""
		Initialize game config service

		:param config:
			Application configuration
		"""
		self._config = config

	def get_supported_games(self) -> list[GameConfig]:
		"""
		Get list of supported game configurations

		:return:
			List of GameConfig objects
		"""
		return self._config.supported_games

	def get_game_config_by_name(self, game_name: str) -> GameConfig | None:
		"""
		Find game config by name

		:param game_name:
			Game name to search for
		:return:
			GameConfig or None if not found
		"""
		for game in self._config.supported_games:
			if game.name == game_name:
				return game
		return None

	def compute_sessions(
		self,
		game_config: GameConfig,
		campaign_session: str | None = None
	) -> list[str]:
		"""
		Compute sessions list based on game config and campaign

		:param game_config:
			Game configuration
		:param campaign_session:
			Optional campaign session name
		:return:
			List of session directory names
		"""
		base_session = game_config.session

		if campaign_session:
			return [base_session, campaign_session]

		return [base_session]

	def compute_saves_pattern(
		self,
		game_config: GameConfig,
		campaign_session: str | None = None
	) -> str:
		"""
		Compute saves pattern by replacing placeholders

		:param game_config:
			Game configuration
		:param campaign_session:
			Optional campaign session name
		:return:
			Resolved saves pattern string
		"""
		pattern = game_config.saves_pattern

		if campaign_session:
			return pattern.replace("{campaign_session}", campaign_session)

		# Remove placeholder if no campaign
		pattern = pattern.replace("{campaign_session}_", "")
		pattern = pattern.replace("_{campaign_session}", "")
		return pattern

	def validate_campaign_session_exists(
		self,
		game_path: str,
		session_dir: str,
		game_data_path: str
	) -> bool:
		"""
		Validate that campaign session directory exists

		:param game_path:
			Game path (relative to game_data_path in Docker, absolute in localhost)
		:param session_dir:
			Session directory name to validate
		:param game_data_path:
			Base game data path (":local" for localhost mode)
		:return:
			True if session directory exists
		"""
		if game_data_path == ":local":
			full_path = os.path.join(game_path, "sessions", session_dir)
		else:
			full_path = os.path.join(game_data_path, game_path, "sessions", session_dir)

		return os.path.isdir(full_path)
