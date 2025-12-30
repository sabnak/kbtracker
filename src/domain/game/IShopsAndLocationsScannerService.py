from abc import ABC, abstractmethod

from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop


class IShopsAndLocationsScannerService(ABC):

	@abstractmethod
	def scan(self, game_id: int, language: str) -> tuple[list[Location], list[Shop]]:
		"""
		Scan and import locations and shops from game files

		:param game_id:
			Game ID to scan
		:param language:
			Language code (rus, eng, ger, pol)
		:return:
			Tuple of (locations, shops) with database IDs
		"""
		pass
