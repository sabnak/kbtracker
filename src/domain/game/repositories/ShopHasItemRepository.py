from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.ShopHasItem import ShopHasItem
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.game.repositories.mappers.ShopHasItemMapper import ShopHasItemMapper


class ShopHasItemRepository(CrudRepository[ShopHasItem, ShopHasItemMapper], IShopHasItemRepository):

	def _entity_to_mapper(self, entity: ShopHasItem) -> ShopHasItemMapper:
		"""
		Convert ShopHasItem entity to ShopHasItemMapper

		:param entity:
			ShopHasItem entity to convert
		:return:
			ShopHasItemMapper instance
		"""
		return ShopHasItemMapper(
			item_id=entity.item_id,
			shop_id=entity.shop_id,
			profile_id=entity.profile_id,
			count=entity.count
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "ShopHasItem"

	def _get_duplicate_identifier(self, entity: ShopHasItem) -> str:
		"""
		Get duplicate identifier for ShopHasItem

		:param entity:
			ShopHasItem entity
		:return:
			Identifier string
		"""
		return f"item_id={entity.item_id}, shop_id={entity.shop_id}, profile_id={entity.profile_id}"

	def create(self, link: ShopHasItem) -> ShopHasItem:
		"""
		Create new shop-item link

		:param link:
			ShopHasItem entity to create
		:return:
			Created link
		"""
		return self._create_single(link)

	def get_by_profile(self, profile_id: int) -> list[ShopHasItem]:
		with self._session_factory() as session:
			mappers = session.query(ShopHasItemMapper).filter(
				ShopHasItemMapper.profile_id == profile_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def get_by_item(
		self,
		item_id: int,
		profile_id: int
	) -> list[ShopHasItem]:
		with self._session_factory() as session:
			mappers = session.query(ShopHasItemMapper).filter(
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
		"""
		Delete shop-item link

		:param item_id:
			Item ID
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
		"""
		with self._session_factory() as session:
			session.query(ShopHasItemMapper).filter(
				ShopHasItemMapper.item_id == item_id,
				ShopHasItemMapper.shop_id == shop_id,
				ShopHasItemMapper.profile_id == profile_id
			).delete()
			session.commit()

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
		with self._session_factory() as session:
			mapper = session.query(ShopHasItemMapper).filter(
				ShopHasItemMapper.item_id == item_id,
				ShopHasItemMapper.shop_id == shop_id,
				ShopHasItemMapper.profile_id == profile_id
			).first()

			if not mapper:
				from src.domain.exceptions import EntityNotFoundException
				raise EntityNotFoundException(
					f"ShopHasItem not found: item_id={item_id}, shop_id={shop_id}, profile_id={profile_id}"
				)

			mapper.count = new_count
			session.commit()
			session.refresh(mapper)

			return self._mapper_to_entity(mapper)

	def _mapper_to_entity(self, mapper: ShopHasItemMapper) -> ShopHasItem:
		return ShopHasItem(
			item_id=mapper.item_id,
			shop_id=mapper.shop_id,
			profile_id=mapper.profile_id,
			count=mapper.count
		)
