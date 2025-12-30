from abc import ABC, abstractmethod
import re

from src.domain.game.entities.Localization import Localization


class ILocalizationScannerService(ABC):

	@abstractmethod
	def scan(
		self,
		sessions_path: str,
		lang: str = 'rus'
	) -> list[Localization]:
		"""
		Scan and import localization entries from game files

		Scans all configured localization files (from config.localization_files)
		and imports them into the database.

		:param sessions_path:
			Absolute path to sessions directory containing .kfs archives
		:param kb_id_pattern:
			Optional regex pattern to match kb_id (must contain 'kb_id' named group)
			Default: ^(?P<kb_id>[-\w]+)
		:param lang:
			Language code (default: 'rus')
		:return:
			List of created Localization entities with database IDs
		"""
		pass
