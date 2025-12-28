from abc import ABC, abstractmethod
from src.domain.game.entities.ObjectHasItem import ObjectHasItem


class IObjectHasItemRepository(ABC):

	@abstractmethod
	def create(self, link: ObjectHasItem) -> ObjectHasItem:
		"""
		Create new item-object link

		:param link:
			Link to create
		:return:
			Created link
		"""
		pass

	@abstractmethod
	def get_by_profile(self, profile_id: int) -> list[ObjectHasItem]:
		"""
		Get all links for a profile

		:param profile_id:
			Profile ID
		:return:
			List of links
		"""
		pass

	@abstractmethod
	def get_by_item(
		self,
		item_id: int,
		profile_id: int
	) -> list[ObjectHasItem]:
		"""
		Get all objects where an item is found for a profile

		:param item_id:
			Item ID
		:param profile_id:
			Profile ID
		:return:
			List of links
		"""
		pass

	@abstractmethod
	def delete(
		self,
		item_id: int,
		object_id: int,
		profile_id: int
	) -> None:
		"""
		Delete item-object link

		:param item_id:
			Item ID
		:param object_id:
			Object ID
		:param profile_id:
			Profile ID
		:return:
		"""
		pass
