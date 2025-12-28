from sqlalchemy.orm import Session
from src.domain.game.entities.Location import Location
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.repositories.mappers.models import LocationModel


class LocationRepository(ILocationRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, location: Location) -> Location:
		model = LocationModel(
			kb_id=location.kb_id,
			name=location.name
		)
		self._session.add(model)
		self._session.commit()
		self._session.refresh(model)
		return self._model_to_entity(model)

	def get_by_id(self, location_id: int) -> Location | None:
		model = self._session.query(LocationModel).filter(
			LocationModel.id == location_id
		).first()
		return self._model_to_entity(model) if model else None

	def get_by_kb_id(self, kb_id: str) -> Location | None:
		model = self._session.query(LocationModel).filter(
			LocationModel.kb_id == kb_id
		).first()
		return self._model_to_entity(model) if model else None

	def list_all(self) -> list[Location]:
		models = self._session.query(LocationModel).all()
		return [self._model_to_entity(m) for m in models]

	def create_batch(self, locations: list[Location]) -> list[Location]:
		models = [
			LocationModel(
				kb_id=loc.kb_id,
				name=loc.name
			)
			for loc in locations
		]
		self._session.add_all(models)
		self._session.commit()
		for model in models:
			self._session.refresh(model)
		return [self._model_to_entity(m) for m in models]

	def _model_to_entity(self, model: LocationModel) -> Location:
		return Location(
			id=model.id,
			kb_id=model.kb_id,
			name=model.name
		)
