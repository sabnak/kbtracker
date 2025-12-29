from sqlalchemy.orm import Session
from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.Shop import Shop
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.repositories.mappers.ShopMapper import ShopMapper


class ShopRepository(CrudRepository[Shop, ShopMapper], IShopRepository):

	def __init__(self, session: Session):
		super().__init__(session)

	def _entity_to_mapper(self, entity: Shop) -> ShopMapper:
		"""
		Convert Shop entity to ShopMapper

		:param entity:
			Shop entity to convert
		:return:
			ShopMapper instance
		"""
		return ShopMapper(
			game_id=entity.game_id,
			kb_id=entity.kb_id,
			location_id=entity.location_id,
			name=entity.name,
			hint=entity.hint,
			msg=entity.msg
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Shop"

	def _get_duplicate_identifier(self, entity: Shop) -> str:
		"""
		Get duplicate identifier for Shop

		:param entity:
			Shop entity
		:return:
			Identifier string
		"""
		return f"game_id={entity.game_id}, kb_id={entity.kb_id}"

	def create(self, shop: Shop) -> Shop:
		"""
		Create new shop

		:param shop:
			Shop entity to create
		:return:
			Created shop with database ID
		"""
		return self._create_single(shop)

	def get_by_id(self, shop_id: int) -> Shop | None:
		mapper = self._session.query(ShopMapper).filter(
			ShopMapper.id == shop_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: int) -> Shop | None:
		mapper = self._session.query(ShopMapper).filter(
			ShopMapper.kb_id == kb_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_location_id(self, location_id: int) -> list[Shop]:
		mappers = self._session.query(ShopMapper).filter(
			ShopMapper.location_id == location_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def list_all(self) -> list[Shop]:
		mappers = self._session.query(ShopMapper).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def create_batch(self, shops: list[Shop]) -> list[Shop]:
		"""
		Create multiple shops

		:param shops:
			List of shop entities to create
		:return:
			List of created shops with database IDs
		"""
		return self._create_batch(shops)

	def _mapper_to_entity(self, mapper: ShopMapper) -> Shop:
		return Shop(
			id=mapper.id,
			game_id=mapper.game_id,
			kb_id=mapper.kb_id,
			location_id=mapper.location_id,
			name=mapper.name,
			hint=mapper.hint,
			msg=mapper.msg
		)
