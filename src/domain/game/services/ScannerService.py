import os.path

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameScanner import IGameScanner
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IObjectRepository import IObjectRepository
from src.domain.game.entities.Item import Item
from src.domain.game.utils.KFSItemsParser import KFSItemsParser


class ScannerService:

	def __init__(
		self,
		item_repository: IItemRepository,
		location_repository: ILocationRepository,
		object_repository: IObjectRepository,
		config: Config = Provide[Container.config]
	):
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._object_repository = object_repository
		self._config = config

	def scan_game_files(
		self,
		game_path: str,
		language: str
	) -> dict[str, int]:
		"""
		Scan game files and populate database

		:param game_path:
			Game path relative to /data directory (e.g., "darkside", "crosswords")
		:param language:
			Language code (rus, eng, ger, pol)
		:param game_data_path:
			Base path to game data
		:return:
			Dictionary with counts of scanned items and objects
		"""
		items = self._parse_items(
			os.path.join(self._config['game_data_path'], game_path, "sessions"),
			language
		)
		self._item_repository.create_batch(items)
		return {
			"items": len(items),
			# "locations": len(created_locations),
			# "objects": len(objects_to_create)
		}

	def _parse_items(self, session_path: str, language: str) -> list[Item]:
		parser = KFSItemsParser(session_path, language)
		return parser.parse()
