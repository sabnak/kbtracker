from sqlalchemy.orm import Session
from src.domain.game.entities.ShopHasItem import ShopHasItem
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.game.repositories.mappers.ShopHasItemMapper import ShopHasItemMapper


class ShopHasItemRepository(IShopHasItemRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, link: ShopHasItem) -> ShopHasItem:
		mapper = ShopHasItemMapper(
			item_id=link.item_id,
			shop_id=link.shop_id,
			profile_id=link.profile_id,
			count=link.count
		)
		self._session.add(mapper)
		self._session.commit()
		return self._mapper_to_entity(mapper)

	def get_by_profile(self, profile_id: int) -> list[ShopHasItem]:
		mappers = self._session.query(ShopHasItemMapper).filter(
			ShopHasItemMapper.profile_id == profile_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def get_by_item(
		self,
		item_id: int,
		profile_id: int
	) -> list[ShopHasItem]:
		mappers = self._session.query(ShopHasItemMapper).filter(
			ShopHasItemMapper.item_id == item_id,
			ShopHasItemMapper.profile_id == profile_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def delete(
		self,
		item_id: int,
		shop_id: int,
		profile_id: int
	) -> None:
		self._session.query(ShopHasItemMapper).filter(
			ShopHasItemMapper.item_id == item_id,
			ShopHasItemMapper.shop_id == shop_id,
			ShopHasItemMapper.profile_id == profile_id
		).delete()
		self._session.commit()

	@staticmethod
	def _mapper_to_entity(mapper: ShopHasItemMapper) -> ShopHasItem:
		return ShopHasItem(
			item_id=mapper.item_id,
			shop_id=mapper.shop_id,
			profile_id=mapper.profile_id,
			count=mapper.count
		)
