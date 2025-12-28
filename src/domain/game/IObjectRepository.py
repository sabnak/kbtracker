from abc import ABC, abstractmethod
from src.domain.game.entities.Object import Object


class IObjectRepository(ABC):

	@abstractmethod
	def create(self, obj: Object) -> Object:
		"""
		Create new object

		:param obj:
			Object to create
		:return:
			Created object with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, object_id: int) -> Object | None:
		"""
		Get object by ID

		:param object_id:
			Object ID
		:return:
			Object or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: int) -> Object | None:
		"""
		Get object by game identifier

		:param kb_id:
			Game identifier
		:return:
			Object or None if not found
		"""
		pass

	@abstractmethod
	def get_by_location_id(self, location_id: int) -> list[Object]:
		"""
		Get all objects in a location

		:param location_id:
			Location ID
		:return:
			List of objects in the location
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[Object]:
		"""
		Get all objects

		:return:
			List of all objects
		"""
		pass

	@abstractmethod
	def create_batch(self, objects: list[Object]) -> list[Object]:
		"""
		Create multiple objects

		:param objects:
			Objects to create
		:return:
			Created objects with IDs
		"""
		pass
