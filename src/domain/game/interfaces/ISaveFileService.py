from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.domain import ProfileEntity
from src.domain.app.entities.Game import Game


class ISaveFileService(ABC):

	@abstractmethod
	def list_save_directories(
		self,
		game: Game,
		limit: int = 100
	) -> dict[str, list[dict]]:
		"""
		List save directories grouped by game name

		:param game:
			Game entity containing saves_pattern
		:param limit:
			Maximum number of saves to return per game
		:return:
			Dictionary with game names as keys and list of save info dicts
		"""
		pass

	@abstractmethod
	def scan_hero_data(
		self,
		game: Game,
		save_identifier: str
	) -> dict[str, str]:
		"""
		Scan save file and extract hero data

		:param game:
			Game entity containing saves_pattern
		:param save_identifier:
			Save identifier to match against wildcard in pattern
		:return:
			Hero data dictionary with first_name, second_name, full_name
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
	def scan_shop_inventory(self, save_path: Path) -> list[dict[str, Any]]:
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
