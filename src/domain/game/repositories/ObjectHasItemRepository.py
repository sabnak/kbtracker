from sqlalchemy.orm import Session
from src.domain.game.entities.ObjectHasItem import ObjectHasItem
from src.domain.game.IObjectHasItemRepository import IObjectHasItemRepository
from src.domain.game.repositories.mappers.ObjectHasItemMapper import ObjectHasItemMapper


class ObjectHasItemRepository(IObjectHasItemRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, link: ObjectHasItem) -> ObjectHasItem:
		mapper = ObjectHasItemMapper(
			item_id=link.item_id,
			object_id=link.object_id,
			profile_id=link.profile_id,
			count=link.count
		)
		self._session.add(mapper)
		self._session.commit()
		return self._mapper_to_entity(mapper)

	def get_by_profile(self, profile_id: int) -> list[ObjectHasItem]:
		mappers = self._session.query(ObjectHasItemMapper).filter(
			ObjectHasItemMapper.profile_id == profile_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def get_by_item(
		self,
		item_id: int,
		profile_id: int
	) -> list[ObjectHasItem]:
		mappers = self._session.query(ObjectHasItemMapper).filter(
			ObjectHasItemMapper.item_id == item_id,
			ObjectHasItemMapper.profile_id == profile_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def delete(
		self,
		item_id: int,
		object_id: int,
		profile_id: int
	) -> None:
		self._session.query(ObjectHasItemMapper).filter(
			ObjectHasItemMapper.item_id == item_id,
			ObjectHasItemMapper.object_id == object_id,
			ObjectHasItemMapper.profile_id == profile_id
		).delete()
		self._session.commit()

	@staticmethod
	def _mapper_to_entity(mapper: ObjectHasItemMapper) -> ObjectHasItem:
		return ObjectHasItem(
			item_id=mapper.item_id,
			object_id=mapper.object_id,
			profile_id=mapper.profile_id,
			count=mapper.count
		)
