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

	def get_available_game_paths(self) -> list[str]:
		"""
		Scan game data directory for available game paths

		:return:
			List of directory names found in game data path,
			empty list if directory doesn't exist or on error
		"""
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
