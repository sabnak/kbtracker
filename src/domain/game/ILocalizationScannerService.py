from abc import ABC, abstractmethod
import re

from src.domain.game.entities.Localization import Localization


class ILocalizationScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, lang: str = 'rus') -> list[Localization]:
		"""
		Scan and import localization entries from game files

		Scans all configured localization files (from config.localization_files)
		and imports them into the database.

		:param game_id:
			Game ID to scan
		:param lang:
			Language code (default: 'rus')
		:return:
			List of created Localization entities with database IDs
		"""
		pass
