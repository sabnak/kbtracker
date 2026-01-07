from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.domain import ProfileEntity


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
	def scan_hero_data(
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

	@abstractmethod
	def find_profile_most_recent_save(self, profile: ProfileEntity) -> Path:
		"""
		Find most recent save file matching profile hash

		:param profile:
			Profile entity
		:return:
			Path to matching save file
		:raises FileNotFoundError:
			If no matching save found
		"""
		...

	@abstractmethod
	def scan_shop_inventory(self, save_path: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
		...

	@abstractmethod
	def compute_hash(self, full_name: str) -> str:
		"""
		Compute hash from hero full name

		:param full_name:
			Hero's full name
		:return:
			Hash as MD5 hex string
		"""
		...
