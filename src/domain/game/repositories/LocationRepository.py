from sqlalchemy.orm import Session
from src.domain.game.entities.Location import Location
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.repositories.mappers.LocationMapper import LocationMapper


class LocationRepository(ILocationRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, location: Location) -> Location:
		mapper = LocationMapper(
			kb_id=location.kb_id,
			name=location.name
		)
		self._session.add(mapper)
		self._session.commit()
		self._session.refresh(mapper)
		return self._mapper_to_entity(mapper)

	def get_by_id(self, location_id: int) -> Location | None:
		mapper = self._session.query(LocationMapper).filter(
			LocationMapper.id == location_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Location | None:
		mapper = self._session.query(LocationMapper).filter(
			LocationMapper.kb_id == kb_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Location]:
		mappers = self._session.query(LocationMapper).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def create_batch(self, locations: list[Location]) -> list[Location]:
		mappers = [
			LocationMapper(
				kb_id=loc.kb_id,
				name=loc.name
			)
			for loc in locations
		]
		self._session.add_all(mappers)
		self._session.commit()
		for mapper in mappers:
			self._session.refresh(mapper)
		return [self._mapper_to_entity(m) for m in mappers]

	@staticmethod
	def _mapper_to_entity(mapper: LocationMapper) -> Location:
		return Location(
			id=mapper.id,
			kb_id=mapper.kb_id,
			name=mapper.name
		)
