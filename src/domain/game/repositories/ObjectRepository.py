from sqlalchemy.orm import Session
from src.domain.game.entities.Object import Object
from src.domain.game.IObjectRepository import IObjectRepository
from src.domain.game.repositories.mappers.models import ObjectModel


class ObjectRepository(IObjectRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, obj: Object) -> Object:
		model = ObjectModel(
			kb_id=obj.kb_id,
			location_id=obj.location_id,
			name=obj.name,
			hint=obj.hint,
			msg=obj.msg
		)
		self._session.add(model)
		self._session.commit()
		self._session.refresh(model)
		return self._model_to_entity(model)

	def get_by_id(self, object_id: int) -> Object | None:
		model = self._session.query(ObjectModel).filter(
			ObjectModel.id == object_id
		).first()
		return self._model_to_entity(model) if model else None

	def get_by_kb_id(self, kb_id: int) -> Object | None:
		model = self._session.query(ObjectModel).filter(
			ObjectModel.kb_id == kb_id
		).first()
		return self._model_to_entity(model) if model else None

	def get_by_location_id(self, location_id: int) -> list[Object]:
		models = self._session.query(ObjectModel).filter(
			ObjectModel.location_id == location_id
		).all()
		return [self._model_to_entity(m) for m in models]

	def list_all(self) -> list[Object]:
		models = self._session.query(ObjectModel).all()
		return [self._model_to_entity(m) for m in models]

	def create_batch(self, objects: list[Object]) -> list[Object]:
		models = [
			ObjectModel(
				kb_id=obj.kb_id,
				location_id=obj.location_id,
				name=obj.name,
				hint=obj.hint,
				msg=obj.msg
			)
			for obj in objects
		]
		self._session.add_all(models)
		self._session.commit()
		for model in models:
			self._session.refresh(model)
		return [self._model_to_entity(m) for m in models]

	def _model_to_entity(self, model: ObjectModel) -> Object:
		return Object(
			id=model.id,
			kb_id=model.kb_id,
			location_id=model.location_id,
			name=model.name,
			hint=model.hint,
			msg=model.msg
		)
