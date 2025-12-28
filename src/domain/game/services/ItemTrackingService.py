from src.domain.game.entities.Item import Item
from src.domain.game.entities.Location import Location
from src.domain.game.entities.Object import Object
from src.domain.game.entities.ObjectHasItem import ObjectHasItem
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IObjectRepository import IObjectRepository
from src.domain.game.IObjectHasItemRepository import IObjectHasItemRepository


class ItemTrackingService:

	def __init__(
		self,
		item_repository: IItemRepository,
		location_repository: ILocationRepository,
		object_repository: IObjectRepository,
		object_has_item_repository: IObjectHasItemRepository
	):
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._object_repository = object_repository
		self._object_has_item_repository = object_has_item_repository

	def search_items(self, query: str) -> list[Item]:
		"""
		Search items by name

		:param query:
			Search query
		:return:
			List of matching items
		"""
		if not query or query.strip() == "":
			return self._item_repository.list_all()
		return self._item_repository.search_by_name(query)

	def get_locations(self) -> list[Location]:
		"""
		Get all locations

		:return:
			List of all locations
		"""
		return self._location_repository.list_all()

	def get_objects_by_location(self, location_id: int) -> list[Object]:
		"""
		Get all objects in a location

		:param location_id:
			Location ID
		:return:
			List of objects
		"""
		return self._object_repository.get_by_location_id(location_id)

	def link_item_to_object(
		self,
		profile_id: int,
		item_id: int,
		object_id: int,
		count: int
	) -> None:
		"""
		Link item to object for a profile

		:param profile_id:
			Profile ID
		:param item_id:
			Item ID
		:param object_id:
			Object ID (merchant)
		:param count:
			Number of items available
		:return:
		"""
		link = ObjectHasItem(
			item_id=item_id,
			object_id=object_id,
			profile_id=profile_id,
			count=count
		)
		self._object_has_item_repository.create(link)

	def get_tracked_items(self, profile_id: int) -> list[dict]:
		"""
		Get all tracked items for a profile with location and object info

		:param profile_id:
			Profile ID
		:return:
			List of dictionaries with item, object, and location data
		"""
		links = self._object_has_item_repository.get_by_profile(profile_id)

		result = []
		for link in links:
			item = self._item_repository.get_by_id(link.item_id)
			obj = self._object_repository.get_by_id(link.object_id)
			location = self._location_repository.get_by_id(obj.location_id) if obj else None

			result.append({
				"item": item,
				"object": obj,
				"location": location,
				"count": link.count
			})

		return result
