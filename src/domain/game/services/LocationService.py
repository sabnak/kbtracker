from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.ILocationService import ILocationService
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop


class LocationService(ILocationService):

	def __init__(
		self,
		location_repository: ILocationRepository = Provide[Container.location_repository],
		shop_repository: IShopRepository = Provide[Container.shop_repository]
	):
		self._location_repository = location_repository
		self._shop_repository = shop_repository

	def get_locations(self) -> list[Location]:
		"""
		Get all locations

		:return:
			List of all locations
		"""
		return self._location_repository.list_all()

	def get_shops_by_location(self, location_id: int) -> list[Shop]:
		"""
		Get all shops in a location

		:param location_id:
			Location ID
		:return:
			List of shops
		"""
		return self._shop_repository.get_by_location_id(location_id)

	def get_shops_grouped_by_location(self) -> list[dict]:
		"""
		Get shops grouped by location

		:return:
			List of locations with their shops
		"""
		locations = self._location_repository.list_all()

		result = []
		for location in locations:
			shops = self._shop_repository.get_by_location_id(location.id)
			result.append({
				"location": location,
				"shops": shops
			})

		return result
