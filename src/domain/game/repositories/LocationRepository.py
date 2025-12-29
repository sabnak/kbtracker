from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.Location import Location
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.repositories.mappers.LocationMapper import LocationMapper


class LocationRepository(CrudRepository[Location, LocationMapper], ILocationRepository):

	def _entity_to_mapper(self, entity: Location) -> LocationMapper:
		"""
		Convert Location entity to LocationMapper

		:param entity:
			Location entity to convert
		:return:
			LocationMapper instance
		"""
		return LocationMapper(
			game_id=entity.game_id,
			kb_id=entity.kb_id,
			name=entity.name
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Location"

	def _get_duplicate_identifier(self, entity: Location) -> str:
		"""
		Get duplicate identifier for Location

		:param entity:
			Location entity
		:return:
			Identifier string
		"""
		return f"game_id={entity.game_id}, kb_id={entity.kb_id}"

	def create(self, location: Location) -> Location:
		"""
		Create new location

		:param location:
			Location entity to create
		:return:
			Created location with database ID
		"""
		return self._create_single(location)

	def get_by_id(self, location_id: int) -> Location | None:
		with self._session_factory() as session:
			mapper = session.query(LocationMapper).filter(
				LocationMapper.id == location_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Location | None:
		with self._session_factory() as session:
			mapper = session.query(LocationMapper).filter(
				LocationMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Location]:
		with self._session_factory() as session:
			mappers = session.query(LocationMapper).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def create_batch(self, locations: list[Location]) -> list[Location]:
		"""
		Create multiple locations

		:param locations:
			List of location entities to create
		:return:
			List of created locations with database IDs
		"""
		return self._create_batch(locations)

	def list_by_game_id(self, game_id: int) -> list[Location]:
		with self._session_factory() as session:
			mappers = session.query(LocationMapper).filter(
				LocationMapper.game_id == game_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def _mapper_to_entity(self, mapper: LocationMapper) -> Location:
		return Location(
			id=mapper.id,
			game_id=mapper.game_id,
			kb_id=mapper.kb_id,
			name=mapper.name
		)
