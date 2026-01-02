from sqlalchemy import func, text, desc, asc
from sqlalchemy.orm import aliased

from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitClass import UnitClass
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
			unit_class=entity.unit_class.value,
			params=entity.params,
			main=entity.main
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

	def _build_query_with_localization(self, session):
		"""
		Build base query with localization JOIN for unit name

		:param session:
			Database session
		:return:
			Tuple of (query, NameLocalization alias)
		"""
		NameLocalization = aliased(LocalizationMapper)

		query = session.query(
			UnitMapper,
			NameLocalization.text.label('loc_name')
		).join(
			NameLocalization,
			NameLocalization.kb_id == func.concat('cpn_', UnitMapper.kb_id)
		)

		return query, NameLocalization

	def _row_to_entity(self, row: tuple) -> Unit:
		"""
		Convert query row with localization to Unit entity

		:param row:
			Tuple of (UnitMapper, name_text)
		:return:
			Unit entity
		:raises LocalizationNotFoundException:
			When name localization is missing
		"""
		mapper, name = row

		if not name:
			raise LocalizationNotFoundException(
				entity_type="Unit",
				kb_id=mapper.kb_id,
				localization_key=f"cpn_{mapper.kb_id}"
			)

		return Unit(
			id=mapper.id,
			kb_id=mapper.kb_id,
			name=name,
			unit_class=UnitClass(mapper.unit_class),
			params=mapper.params,
			main=mapper.main
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
		Get unit by ID with localized name

		:param unit_id:
			Unit ID
		:return:
			Unit or None
		"""
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			row = query.filter(UnitMapper.id == unit_id).first()
			return self._row_to_entity(row) if row else None

	def get_by_kb_id(self, kb_id: str) -> Unit | None:
		"""
		Get unit by kb_id with localized name

		:param kb_id:
			Unit kb_id
		:return:
			Unit or None
		"""
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			row = query.filter(UnitMapper.kb_id == kb_id).first()
			return self._row_to_entity(row) if row else None

	def list_all(self, sort_by: str = "name", sort_order: str = "asc") -> list[Unit]:
		"""
		Get all units with localized names

		:param sort_by:
			Field to sort by
		:param sort_order:
			Sort direction
		:return:
			List of units
		"""
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			query = self._apply_sorting(query, sort_by, sort_order)
			rows = query.all()
			return [self._row_to_entity(row) for row in rows]

	def search_by_name(self, query_str: str) -> list[Unit]:
		"""
		Search units by name

		:param query_str:
			Search query
		:return:
			List of matching units
		"""
		with self._get_session() as session:
			query, NameLocalization = self._build_query_with_localization(session)
			rows = query.filter(
				NameLocalization.text.ilike(f"%{query_str}%")
			).all()
			return [self._row_to_entity(row) for row in rows]

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
			SQLAlchemy query with localization joins
		:param sort_by:
			Field to sort by (name, kb_id)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		if sort_by == "name":
			sort_column = text('loc_name')
		elif sort_by == "kb_id":
			sort_column = UnitMapper.kb_id
		else:
			sort_column = text('loc_name')

		if sort_order.lower() == "desc":
			return query.order_by(desc(sort_column))
		else:
			return query.order_by(asc(sort_column))

	def _mapper_to_entity(self, mapper: UnitMapper) -> Unit:
		"""
		Convert UnitMapper to Unit entity

		Note: This method fetches full entity with localization

		:param mapper:
			UnitMapper to convert
		:return:
			Unit entity with localized name
		"""
		return self.get_by_id(mapper.id)
