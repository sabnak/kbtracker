import os.path

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.dto.ScanResults import ScanResults
from src.domain.game.entities.ItemSet import ItemSet
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop
from src.domain.game.services.LocalizationScannerService import LocalizationScannerService
from src.domain.game.utils.KFSItemsParser import KFSItemsParser
from src.domain.game.utils.KFSLocationsAndShopsParser import KFSLocationsAndShopsParser


class ScannerService:

	def __init__(
		self,
		game_repository: IGameRepository,
		item_repository: IItemRepository,
		item_set_repository: IItemSetRepository,
		location_repository: ILocationRepository,
		shop_repository: IShopRepository,
		localization_service: LocalizationScannerService = Provide[Container.localization_scanner_service],
		config: Config = Provide[Container.config]
	):
		self._game_repository = game_repository
		self._item_repository = item_repository
		self._item_set_repository = item_set_repository
		self._location_repository = location_repository
		self._shop_repository = shop_repository
		self._localization_scanner = localization_service
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
			ScanResults with counts of scanned items, locations, shops, and sets
		"""
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		sessions_path = os.path.join(self._config.game_data_path, game.path, "sessions")

		localizations_string = len(self._localization_scanner.scan(game_id, language))

		parse_results = self._parse_items_and_sets(sessions_path)

		total_items = 0
		total_sets = 0

		for set_kb_id, set_data in parse_results.items():
			if set_kb_id == "setless":
				items = set_data["items"]
				self._item_repository.create_batch(items)
				total_items += len(items)
			else:
				item_set = ItemSet(
					id=0,
					kb_id=set_kb_id
				)
				created_set = self._item_set_repository.create(item_set)
				total_sets += 1

				items = set_data["items"]
				for item in items:
					item.item_set_id = created_set.id
				self._item_repository.create_batch(items)
				total_items += len(items)

		locations, shops = self._parse_locations_and_shops(sessions_path, language)

		return ScanResults(
			items=total_items,
			locations=len(locations),
			shops=len(shops),
			sets=total_sets,
			localizations=localizations_string
		)

	def _parse_items_and_sets(self, session_path: str) -> dict[str, dict[str, any]]:
		"""
		Parse items and sets from game files

		:param session_path:
			Path to sessions directory
		:return:
			Dictionary with sets and items grouped by set membership
		"""
		parser = KFSItemsParser(session_path)
		return parser.parse()

	def _parse_locations_and_shops(
		self,
		session_path: str,
		language: str
	) -> tuple[list[Location], list[Shop]]:
		"""
		Parse locations and shops from game files

		Parses locations and shops, saves locations first to get DB IDs,
		then updates shop location_ids with real DB IDs before saving.

		:param session_path:
			Path to sessions directory
		:param language:
			Language code
		:return:
			Tuple of (saved_locations, saved_shops)
		"""
		parser = KFSLocationsAndShopsParser(session_path, language)
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
