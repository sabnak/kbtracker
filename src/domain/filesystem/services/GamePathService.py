import os

from src.domain.filesystem.IGamePathService import IGamePathService


class GamePathService(IGamePathService):

	def __init__(self, game_data_path: str):
		"""
		Initialize game path service

		:param game_data_path:
			Path to game data directory (e.g., "/data")
		"""
		self._game_data_path = game_data_path

	def is_localhost_mode(self) -> bool:
		"""
		Check if running in localhost mode

		:return:
			True if game_data_path is ":local", False otherwise
		"""
		return self._game_data_path == ":local"

	def get_available_game_paths(self) -> list[str]:
		"""
		Scan game data directory for available game paths

		:return:
			List of directory names found in game data path,
			empty list if in localhost mode, directory doesn't exist, or on error
		"""
		if self.is_localhost_mode():
			return []

		try:
			if not os.path.exists(self._game_data_path):
				return []

			entries = os.listdir(self._game_data_path)

			directories = [
				entry for entry in entries
				if os.path.isdir(os.path.join(self._game_data_path, entry))
			]

			return sorted(directories)

		except (OSError, PermissionError):
			return []

	def validate_game_path(self, path: str) -> bool:
		"""
		Validate that a game path exists and appears to contain game data

		:param path:
			Absolute path to game directory to validate
		:return:
			True if path exists and contains sessions directory, False otherwise
		"""
		if not path or not os.path.isabs(path):
			return False

		if not os.path.exists(path):
			return False

		if not os.path.isdir(path):
			return False

		sessions_path = os.path.join(path, "sessions")
		return os.path.exists(sessions_path) and os.path.isdir(sessions_path)
