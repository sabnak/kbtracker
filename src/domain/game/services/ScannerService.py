import os.path

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.entities.Item import Item
from src.domain.game.utils.KFSItemsParser import KFSItemsParser


class ScannerService:

	def __init__(
		self,
		game_repository: IGameRepository,
		item_repository: IItemRepository,
		location_repository: ILocationRepository,
		shop_repository: IShopRepository,
		config: Config = Provide[Container.config]
	):
		self._game_repository = game_repository
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._shop_repository = shop_repository
		self._config = config

	def scan_game_files(
		self,
		game_id: int,
		language: str
	) -> dict[str, int]:
		"""
		Scan game files and populate database

		:param game_id:
			Game ID to scan
		:param language:
			Language code (rus, eng, ger, pol)
		:return:
			Dictionary with counts of scanned items and shops
		"""
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		items = self._parse_items(
			os.path.join(self._config['game_data_path'], game.path, "sessions"),
			language,
			game_id
		)
		self._item_repository.create_batch(items)
		return {
			"items": len(items),
			# "locations": len(created_locations),
			# "shops": len(shops_to_create)
		}

	def _parse_items(
		self,
		session_path: str,
		language: str,
		game_id: int
	) -> list[Item]:
		parser = KFSItemsParser(session_path, language, game_id)
		return parser.parse()
