from abc import ABC, abstractmethod

from src.core.GameConfig import GameConfig


class IGameConfigService(ABC):

	@abstractmethod
	def get_supported_games(self) -> list[GameConfig]:
		"""
		Get list of supported game configurations

		:return:
			List of GameConfig objects
		"""
		pass

	@abstractmethod
	def get_game_config_by_name(self, game_name: str) -> GameConfig | None:
		"""
		Find game config by name

		:param game_name:
			Game name to search for
		:return:
			GameConfig or None if not found
		"""
		pass

	@abstractmethod
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
		pass

	@abstractmethod
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
		pass

	@abstractmethod
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
		pass
