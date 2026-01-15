import typing

from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.ShopProduct import ShopProduct
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.repositories.mappers.ShopInventoryMapper import ShopInventoryMapper


class ShopInventoryRepository(CrudRepository[ShopProduct, ShopInventoryMapper], IShopInventoryRepository):

	def _entity_to_mapper(self, entity: ShopProduct) -> ShopInventoryMapper:
		"""
		Convert ShopProduct entity to ShopInventoryMapper

		:param entity:
			ShopProduct entity to convert
		:return:
			ShopInventoryMapper instance
		"""
		return ShopInventoryMapper(
			product_id=entity.product_id,
			product_type=entity.product_type,
			count=entity.count,
			shop_id=entity.shop_id,
			shop_type=entity.shop_type,
			location=entity.location,
			profile_id=entity.profile_id
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "ShopProduct"

	def _get_duplicate_identifier(self, product: ShopProduct) -> str:
		"""
		Get duplicate identifier for ShopProduct

		:param product:
			ShopProduct entity
		:return:
			Identifier string
		"""
		return (f"product_id={product.product_id}, product_type={product.product_type.value}, "
		        f"shop_id={product.shop_id}, shop_type={product.shop_type.value}, location={product.location}, "
		        f"profile_id={product.profile_id}")

	def create(self, inventory: ShopProduct) -> ShopProduct:
		"""
		Create new shop inventory entry

		:param inventory:
			ShopProduct entity to create
		:return:
			Created inventory entry
		"""
		return self._create_single(inventory)

	def get_by_profile(
		self,
		profile_id: int,
		product_types: typing.Iterable[ShopProductType] = None
	) -> list[ShopProduct]:
		"""
		Get all inventory entries for a profile, optionally filtered by type

		:param profile_id:
			Profile ID
		:param product_types:
			Optional inventory type filter
		:return:
			List of inventory entries
		"""
		with self._get_session() as session:
			query = session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.profile_id == profile_id
			)
			if product_types:
				query = query.filter(ShopInventoryMapper.product_type.in_(product_types))
			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def get_by_entity(
		self,
		product_id: int,
		product_type: ShopProductType,
		profile_id: int
	) -> list[ShopProduct]:
		"""
		Get all shops where an entity is found for a profile

		:param product_id:
			Entity ID
		:param product_type:
			Entity type
		:param profile_id:
			Profile ID
		:return:
			List of inventory entries
		"""
		with self._get_session() as session:
			mappers = session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.product_id == product_id,
				ShopInventoryMapper.product_type == product_type,
				ShopInventoryMapper.profile_id == profile_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def delete(self, product_id: int) -> None:
		"""
		Delete shop inventory entry

		:param product_id:
			Entity ID
		:return:
		"""
		with self._get_session() as session:
			session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.product_id == product_id
			).delete()
			session.commit()

	def delete_by_profile(self, profile_id: int) -> None:
		"""
		Delete all shop inventory entries for a profile

		:param profile_id:
			Profile ID
		:return:
		"""
		with self._get_session() as session:
			session.query(ShopInventoryMapper).filter(
				ShopInventoryMapper.profile_id == profile_id
			).delete()
			session.commit()

	def _mapper_to_entity(self, mapper: ShopInventoryMapper) -> ShopProduct:
		"""
		Convert ShopInventoryMapper to ShopProduct entity

		:param mapper:
			ShopInventoryMapper instance to convert
		:return:
			ShopProduct entity
		"""
		return PydanticEntityFactory.create_entity(ShopProduct, mapper)
