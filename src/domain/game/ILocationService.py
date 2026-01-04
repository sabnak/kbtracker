from abc import ABC, abstractmethod

from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop


class ILocationService(ABC):

	@abstractmethod
	def get_locations(self) -> list[Location]:
		"""
		Get all locations

		:return:
			List of all locations
		"""
		pass

	@abstractmethod
	def get_shops_by_location(self, location_id: int) -> list[Shop]:
		"""
		Get all shops in a location

		:param location_id:
			Location ID
		:return:
			List of shops
		"""
		pass

	@abstractmethod
	def get_shops_grouped_by_location(self) -> list[dict]:
		"""
		Get shops grouped by location

		:return:
			List of locations with their shops
		"""
		pass
