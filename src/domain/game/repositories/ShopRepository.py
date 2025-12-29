from sqlalchemy.orm import Session
from src.domain.game.entities.Shop import Shop
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.repositories.mappers.ShopMapper import ShopMapper


class ShopRepository(IShopRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, shop: Shop) -> Shop:
		mapper = ShopMapper(
			kb_id=shop.kb_id,
			location_id=shop.location_id,
			name=shop.name,
			hint=shop.hint,
			msg=shop.msg
		)
		self._session.add(mapper)
		self._session.commit()
		self._session.refresh(mapper)
		return self._mapper_to_entity(mapper)

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
		mappers = [
			ShopMapper(
				kb_id=obj.kb_id,
				location_id=obj.location_id,
				name=obj.name,
				hint=obj.hint,
				msg=obj.msg
			)
			for obj in shops
		]
		self._session.add_all(mappers)
		self._session.commit()
		for mapper in mappers:
			self._session.refresh(mapper)
		return [self._mapper_to_entity(m) for m in mappers]

	@staticmethod
	def _mapper_to_entity(mapper: ShopMapper) -> Shop:
		return Shop(
			id=mapper.id,
			kb_id=mapper.kb_id,
			location_id=mapper.location_id,
			name=mapper.name,
			hint=mapper.hint,
			msg=mapper.msg
		)
