from abc import ABC, abstractmethod


class ISaveFileService(ABC):

	@abstractmethod
	def list_save_directories(
		self,
		game_path: str,
		limit: int = 100
	) -> dict[str, list[dict]]:
		"""
		List save directories grouped by game name

		:param game_path:
			Game path (e.g., "Darkside")
		:param limit:
			Maximum number of saves to return per game
		:return:
			Dictionary with game names as keys and list of save info dicts
		"""
		pass

	@abstractmethod
	def scan_save_file(
		self,
		game_path: str,
		save_dir_name: str
	) -> dict[str, str]:
		"""
		Scan save file and extract campaign data

		:param game_path:
			Game path (e.g., "Darkside")
		:param save_dir_name:
			Save directory name (timestamp like "1707047253")
		:return:
			Campaign data dictionary with campaign_id, full_name, etc.
		"""
		pass
