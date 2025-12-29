import os.path

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.dto.ScanResults import ScanResults
from src.domain.game.entities.Item import Item
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop
from src.domain.game.utils.KFSItemsParser import KFSItemsParser
from src.domain.game.utils.KFSLocationsAndShopsParser import KFSLocationsAndShopsParser


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
	) -> ScanResults:
		"""
		Scan game files and populate database

		:param game_id:
			Game ID to scan
		:param language:
			Language code (rus, eng, ger, pol)
		:return:
			ScanResults with counts of scanned items, locations, and shops
		"""
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		sessions_path = os.path.join(self._config['game_data_path'], game.path, "sessions")

		# Parse and save items
		items = self._parse_items(sessions_path, language, game_id)
		self._item_repository.create_batch(items)

		# Parse and save locations and shops
		locations, shops = self._parse_locations_and_shops(sessions_path, language, game_id)

		return ScanResults(
			items=len(items),
			locations=len(locations),
			shops=len(shops)
		)

	def _parse_items(
		self,
		session_path: str,
		language: str,
		game_id: int
	) -> list[Item]:
		parser = KFSItemsParser(session_path, language, game_id)
		return parser.parse()

	def _parse_locations_and_shops(
		self,
		session_path: str,
		language: str,
		game_id: int
	) -> tuple[list[Location], list[Shop]]:
		"""
		Parse locations and shops from game files

		Parses locations and shops, saves locations first to get DB IDs,
		then updates shop location_ids with real DB IDs before saving.

		:param session_path:
			Path to sessions directory
		:param language:
			Language code
		:param game_id:
			Game ID
		:return:
			Tuple of (saved_locations, saved_shops)
		"""
		parser = KFSLocationsAndShopsParser(session_path, language, game_id)
		results = parser.parse()

		saved_locations = []
		saved_shops = []

		for entry in results:
			location = entry['location']
			shops = entry['shops']

			# Save location first to get real DB ID
			created_location = self._location_repository.create(location)
			saved_locations.append(created_location)

			# Update all shops with the real location_id
			for shop in shops:
				shop.location_id = created_location.id

			# Save all shops for this location
			created_shops = self._shop_repository.create_batch(shops)
			saved_shops.extend(created_shops)

		return saved_locations, saved_shops
