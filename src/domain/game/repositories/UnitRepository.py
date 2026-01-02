from sqlalchemy import func, text, desc, asc
from sqlalchemy.orm import aliased

from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.entities.UnitMovetype import UnitMovetype
from src.domain.game.IUnitRepository import IUnitRepository
from src.domain.game.repositories.mappers.UnitMapper import UnitMapper
from src.domain.game.repositories.mappers.LocalizationMapper import LocalizationMapper
from src.domain.exceptions import LocalizationNotFoundException


class UnitRepository(CrudRepository[Unit, UnitMapper], IUnitRepository):

	def _entity_to_mapper(self, entity: Unit) -> UnitMapper:
		"""
		Convert Unit entity to UnitMapper

		:param entity:
			Unit entity to convert
		:return:
			UnitMapper instance
		"""
		return UnitMapper(
			kb_id=entity.kb_id,
			name=entity.name,
			unit_class=entity.unit_class.value,
			params=entity.params,
			main=entity.main,
			cost=entity.cost,
			krit=entity.krit,
			race=entity.race,
			level=entity.level,
			speed=entity.speed,
			attack=entity.attack,
			defense=entity.defense,
			hitback=entity.hitback,
			hitpoint=entity.hitpoint,
			movetype=entity.movetype.value if entity.movetype else None,
			defenseup=entity.defenseup,
			initiative=entity.initiative,
			leadership=entity.leadership,
			resistance=entity.resistance,
			features=entity.features,
			attacks=entity.attacks
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Unit"

	def _get_duplicate_identifier(self, entity: Unit) -> str:
		"""
		Get duplicate identifier for Unit

		:param entity:
			Unit entity
		:return:
			Identifier string
		"""
		return f"kb_id={entity.kb_id}"

	def _mapper_to_entity(self, mapper: UnitMapper) -> Unit:
		"""
		Convert UnitMapper to Unit entity

		:param mapper:
			UnitMapper to convert
		:return:
			Unit entity
		"""
		return Unit(
			id=mapper.id,
			kb_id=mapper.kb_id,
			name=mapper.name,
			unit_class=UnitClass(mapper.unit_class),
			params=mapper.params,
			main=mapper.main,
			cost=mapper.cost,
			krit=mapper.krit,
			race=mapper.race,
			level=mapper.level,
			speed=mapper.speed,
			attack=mapper.attack,
			defense=mapper.defense,
			hitback=mapper.hitback,
			hitpoint=mapper.hitpoint,
			movetype=UnitMovetype(mapper.movetype) if mapper.movetype is not None else None,
			defenseup=mapper.defenseup,
			initiative=mapper.initiative,
			leadership=mapper.leadership,
			resistance=mapper.resistance,
			features=mapper.features,
			attacks=mapper.attacks
		)

	def create(self, unit: Unit) -> Unit:
		"""
		Create new unit

		:param unit:
			Unit entity to create
		:return:
			Created unit with database ID
		"""
		return self._create_single(unit)

	def get_by_id(self, unit_id: int) -> Unit | None:
		"""
		Get unit by ID

		:param unit_id:
			Unit ID
		:return:
			Unit or None
		"""
		with self._get_session() as session:
			mapper = session.query(UnitMapper).filter(UnitMapper.id == unit_id).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Unit | None:
		"""
		Get unit by kb_id

		:param kb_id:
			Unit kb_id
		:return:
			Unit or None
		"""
		with self._get_session() as session:
			mapper = session.query(UnitMapper).filter(UnitMapper.kb_id == kb_id).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self, sort_by: str = "name", sort_order: str = "asc") -> list[Unit]:
		"""
		Get all units

		:param sort_by:
			Field to sort by
		:param sort_order:
			Sort direction
		:return:
			List of units
		"""
		with self._get_session() as session:
			query = session.query(UnitMapper)
			query = self._apply_sorting(query, sort_by, sort_order)
			mappers = query.all()
			return [self._mapper_to_entity(mapper) for mapper in mappers]

	def search_by_name(self, query_str: str) -> list[Unit]:
		"""
		Search units by name

		:param query_str:
			Search query
		:return:
			List of matching units
		"""
		with self._get_session() as session:
			mappers = session.query(UnitMapper).filter(
				UnitMapper.name.ilike(f"%{query_str}%")
			).all()
			return [self._mapper_to_entity(mapper) for mapper in mappers]

	def create_batch(self, units: list[Unit]) -> list[Unit]:
		"""
		Create multiple units

		:param units:
			List of unit entities to create
		:return:
			List of created units with database IDs
		"""
		return self._create_batch(units)

	def _apply_sorting(self, query, sort_by: str, sort_order: str):
		"""
		Apply ORDER BY clause to query

		:param query:
			SQLAlchemy query
		:param sort_by:
			Field to sort by (name, kb_id)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		if sort_by == "name":
			sort_column = UnitMapper.name
		elif sort_by == "kb_id":
			sort_column = UnitMapper.kb_id
		else:
			sort_column = UnitMapper.name

		if sort_order.lower() == "desc":
			return query.order_by(desc(sort_column))
		else:
			return query.order_by(asc(sort_column))
