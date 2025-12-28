from sqlalchemy.orm import Session
from src.domain.game.entities.ObjectHasItem import ObjectHasItem
from src.domain.game.IObjectHasItemRepository import IObjectHasItemRepository
from src.domain.game.repositories.mappers.models import ObjectHasItemModel


class ObjectHasItemRepository(IObjectHasItemRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, link: ObjectHasItem) -> ObjectHasItem:
		model = ObjectHasItemModel(
			item_id=link.item_id,
			object_id=link.object_id,
			profile_id=link.profile_id,
			count=link.count
		)
		self._session.add(model)
		self._session.commit()
		return self._model_to_entity(model)

	def get_by_profile(self, profile_id: int) -> list[ObjectHasItem]:
		models = self._session.query(ObjectHasItemModel).filter(
			ObjectHasItemModel.profile_id == profile_id
		).all()
		return [self._model_to_entity(m) for m in models]

	def get_by_item(
		self,
		item_id: int,
		profile_id: int
	) -> list[ObjectHasItem]:
		models = self._session.query(ObjectHasItemModel).filter(
			ObjectHasItemModel.item_id == item_id,
			ObjectHasItemModel.profile_id == profile_id
		).all()
		return [self._model_to_entity(m) for m in models]

	def delete(
		self,
		item_id: int,
		object_id: int,
		profile_id: int
	) -> None:
		self._session.query(ObjectHasItemModel).filter(
			ObjectHasItemModel.item_id == item_id,
			ObjectHasItemModel.object_id == object_id,
			ObjectHasItemModel.profile_id == profile_id
		).delete()
		self._session.commit()

	def _model_to_entity(self, model: ObjectHasItemModel) -> ObjectHasItem:
		return ObjectHasItem(
			item_id=model.item_id,
			object_id=model.object_id,
			profile_id=model.profile_id,
			count=model.count
		)
