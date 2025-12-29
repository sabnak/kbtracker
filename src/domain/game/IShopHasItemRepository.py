from abc import ABC, abstractmethod
from src.domain.game.entities.ShopHasItem import ShopHasItem


class IShopHasItemRepository(ABC):

	@abstractmethod
	def create(self, link: ShopHasItem) -> ShopHasItem:
		"""
		Create new item-shop link

		:param link:
			Link to create
		:return:
			Created link
		"""
		pass

	@abstractmethod
	def get_by_profile(self, profile_id: int) -> list[ShopHasItem]:
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
	) -> list[ShopHasItem]:
		"""
		Get all shops where an item is found for a profile

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
		shop_id: int,
		profile_id: int
	) -> None:
		"""
		Delete item-shop link

		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
		"""
		pass

	@abstractmethod
	def update_count(
		self,
		item_id: int,
		shop_id: int,
		profile_id: int,
		new_count: int
	) -> ShopHasItem:
		"""
		Update count for item-shop link

		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:param new_count:
			New count value
		:return:
			Updated link
		"""
		pass
