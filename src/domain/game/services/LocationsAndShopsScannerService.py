import os

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.IShopsAndLocationsScannerService import IShopsAndLocationsScannerService
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop
from src.domain.game.parsers.game_data.IKFSLocationsAndShopsParser import IKFSLocationsAndShopsParser


class LocationsAndShopsScannerService(IShopsAndLocationsScannerService):

	def __init__(
		self,
		location_repository: ILocationRepository = Provide[Container.location_repository],
		shop_repository: IShopRepository = Provide[Container.shop_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: IKFSLocationsAndShopsParser = Provide[Container.kfs_locations_and_shops_parser],
		config: Config = Provide[Container.config]
	):
		self._location_repository = location_repository
		self._shop_repository = shop_repository
		self._game_repository = game_repository
		self._parser = parser
		self._config = config

	def scan(self, game_id: int, language: str) -> tuple[list[Location], list[Shop]]:
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		sessions_path = os.path.join(self._config.game_data_path, game.path, "sessions")
		results = self._parser.parse(sessions_path, language)

		saved_locations = []
		saved_shops = []

		for entry in results:
			location = entry['location']
			shops = entry['shops']

			created_location = self._location_repository.create(location)
			saved_locations.append(created_location)

			for shop in shops:
				shop.location_id = created_location.id

			created_shops = self._shop_repository.create_batch(shops)
			saved_shops.extend(created_shops)

		return saved_locations, saved_shops
