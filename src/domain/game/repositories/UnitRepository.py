from sqlalchemy import desc, asc

from src.domain.base.factories.PydanticEntityFactory import PydanticEntityFactory
from src.domain.base.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.entities.UnitMovetype import UnitMovetype
from src.domain.game.interfaces.IUnitRepository import IUnitRepository
from src.domain.game.repositories.mappers.UnitMapper import UnitMapper


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
		return PydanticEntityFactory.create_entity(
			Unit,
			mapper,
			unit_class=UnitClass(mapper.unit_class),
			movetype=UnitMovetype(mapper.movetype) if mapper.movetype else None
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

	def list_all(
		self,
		sort_by: str = "name",
		sort_order: str = "asc",
		unit_class: UnitClass | None = None
	) -> list[Unit]:
		"""
		Get all units

		:param sort_by:
			Field to sort by
		:param sort_order:
			Sort direction
		:param unit_class:
			Optional filter by unit class
		:return:
			List of units
		"""
		with self._get_session() as session:
			query = session.query(UnitMapper)

			if unit_class:
				query = query.filter(UnitMapper.unit_class == unit_class.value)

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

	def search_with_filters(
		self,
		unit_class: UnitClass | None = None,
		sort_by: str = "name",
		sort_order: str = "asc",
		profile_id: int | None = None,
		min_cost: int | None = None,
		max_cost: int | None = None
	) -> list[Unit]:
		"""
		Search units with filter criteria

		:param unit_class:
			Optional unit class filter
		:param sort_by:
			Field to sort by
		:param sort_order:
			Sort direction (asc, desc)
		:param profile_id:
			Optional profile ID filter (shows only units in shop inventory for profile)
		:param min_cost:
			Optional minimum cost filter
		:param max_cost:
			Optional maximum cost filter
		:return:
			List of units matching all provided criteria
		"""
		with self._get_session() as session:
			query = session.query(UnitMapper)

			# Filter by profile_id (JOIN with shop inventory)
			if profile_id is not None:
				from src.domain.game.repositories.mappers.ShopInventoryMapper import ShopInventoryMapper
				from src.domain.game.entities.ShopProductType import ShopProductType

				query = query.join(
					ShopInventoryMapper,
					(ShopInventoryMapper.product_id == UnitMapper.id) &
					(ShopInventoryMapper.product_type.in_([ShopProductType.UNIT, ShopProductType.GARRISON])) &
					(ShopInventoryMapper.profile_id == profile_id)
				).distinct()

			# Filter by unit class
			if unit_class:
				query = query.filter(UnitMapper.unit_class == unit_class.value)

			# Filter by cost range
			if min_cost is not None:
				query = query.filter(UnitMapper.cost >= min_cost)
			if max_cost is not None:
				query = query.filter(UnitMapper.cost <= max_cost)

			# Apply sorting
			query = self._apply_sorting(query, sort_by, sort_order)

			mappers = query.all()
			return [self._mapper_to_entity(mapper) for mapper in mappers]

	def get_by_ids(self, ids: list[int]) -> dict[int, Unit]:
		"""
		Batch fetch units by IDs

		:param ids:
			List of unit IDs
		:return:
			Dictionary mapping ID to Unit
		"""
		if not ids:
			return {}

		with self._get_session() as session:
			mappers = session.query(UnitMapper).filter(UnitMapper.id.in_(ids)).all()

			result = {}
			for mapper in mappers:
				unit = self._mapper_to_entity(mapper)
				result[unit.id] = unit

			return result

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
			Field to sort by (name, kb_id, level, race, cost, leadership, attack, defense, speed, initiative)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		sort_column_map = {
			"name": UnitMapper.name,
			"kb_id": UnitMapper.kb_id,
			"level": UnitMapper.level,
			"race": UnitMapper.race,
			"cost": UnitMapper.cost,
			"leadership": UnitMapper.leadership,
			"attack": UnitMapper.attack,
			"defense": UnitMapper.defense,
			"speed": UnitMapper.speed,
			"initiative": UnitMapper.initiative
		}

		sort_column = sort_column_map.get(sort_by, UnitMapper.name)

		if sort_order.lower() == "desc":
			return query.order_by(desc(sort_column))
		else:
			return query.order_by(asc(sort_column))
