from abc import ABC, abstractmethod


class IGamePathService(ABC):

	@abstractmethod
	def is_localhost_mode(self) -> bool:
		"""
		Check if running in localhost mode

		:return:
			True if in localhost mode, False otherwise
		"""
		pass

	@abstractmethod
	def get_available_game_paths(self) -> list[str]:
		"""
		Get list of available game paths from data directory

		:return:
			List of directory names, empty if none found or error
		"""
		pass

	@abstractmethod
	def validate_game_path(self, path: str) -> bool:
		"""
		Validate that a game path exists and appears to contain game data

		:param path:
			Absolute path to game directory to validate
		:return:
			True if valid game path, False otherwise
		"""
		pass
