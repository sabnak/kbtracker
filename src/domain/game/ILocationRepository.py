from abc import ABC, abstractmethod
from src.domain.game.entities.Location import Location


class ILocationRepository(ABC):

	@abstractmethod
	def create(self, location: Location) -> Location:
		"""
		Create new location

		:param location:
			Location to create
		:return:
			Created location with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, location_id: int) -> Location | None:
		"""
		Get location by ID

		:param location_id:
			Location ID
		:return:
			Location or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> Location | None:
		"""
		Get location by game identifier

		:param kb_id:
			Game identifier
		:return:
			Location or None if not found
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[Location]:
		"""
		Get all locations

		:return:
			List of all locations
		"""
		pass

	@abstractmethod
	def create_batch(self, locations: list[Location]) -> list[Location]:
		"""
		Create multiple locations

		:param locations:
			Locations to create
		:return:
			Created locations with IDs
		"""
		pass
