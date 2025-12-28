from sqlalchemy.orm import Session
from src.domain.game.entities.Object import Object
from src.domain.game.IObjectRepository import IObjectRepository
from src.domain.game.repositories.mappers.ObjectMapper import ObjectMapper


class ObjectRepository(IObjectRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, obj: Object) -> Object:
		mapper = ObjectMapper(
			kb_id=obj.kb_id,
			location_id=obj.location_id,
			name=obj.name,
			hint=obj.hint,
			msg=obj.msg
		)
		self._session.add(mapper)
		self._session.commit()
		self._session.refresh(mapper)
		return self._mapper_to_entity(mapper)

	def get_by_id(self, object_id: int) -> Object | None:
		mapper = self._session.query(ObjectMapper).filter(
			ObjectMapper.id == object_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: int) -> Object | None:
		mapper = self._session.query(ObjectMapper).filter(
			ObjectMapper.kb_id == kb_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_location_id(self, location_id: int) -> list[Object]:
		mappers = self._session.query(ObjectMapper).filter(
			ObjectMapper.location_id == location_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def list_all(self) -> list[Object]:
		mappers = self._session.query(ObjectMapper).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def create_batch(self, objects: list[Object]) -> list[Object]:
		mappers = [
			ObjectMapper(
				kb_id=obj.kb_id,
				location_id=obj.location_id,
				name=obj.name,
				hint=obj.hint,
				msg=obj.msg
			)
			for obj in objects
		]
		self._session.add_all(mappers)
		self._session.commit()
		for mapper in mappers:
			self._session.refresh(mapper)
		return [self._mapper_to_entity(m) for m in mappers]

	@staticmethod
	def _mapper_to_entity(mapper: ObjectMapper) -> Object:
		return Object(
			id=mapper.id,
			kb_id=mapper.kb_id,
			location_id=mapper.location_id,
			name=mapper.name,
			hint=mapper.hint,
			msg=mapper.msg
		)
