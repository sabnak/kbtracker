from sqlalchemy import func
from sqlalchemy.orm import aliased

from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.exceptions import InvalidPropbitException, LocalizationNotFoundException
from src.domain.game.entities.Item import Item
from src.domain.game.entities.Propbit import Propbit
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.repositories.mappers.ItemMapper import ItemMapper
from src.domain.game.repositories.mappers.LocalizationMapper import LocalizationMapper


class ItemRepository(CrudRepository[Item, ItemMapper], IItemRepository):

	def _entity_to_mapper(self, entity: Item) -> ItemMapper:
		"""
		Convert Item entity to ItemMapper

		:param entity:
			Item entity to convert
		:return:
			ItemMapper instance
		"""
		propbits_str = None
		if entity.propbits is not None:
			propbits_str = self._convert_propbits_to_strings(entity.propbits)

		return ItemMapper(
			item_set_id=entity.item_set_id,
			kb_id=entity.kb_id,
			price=entity.price,
			propbits=propbits_str,
			tiers=entity.tiers,
			level=entity.level
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Item"

	def _get_duplicate_identifier(self, entity: Item) -> str:
		"""
		Get duplicate identifier for Item

		:param entity:
			Item entity
		:return:
			Identifier string
		"""
		return f"kb_id={entity.kb_id}"

	def _build_query_with_localization(self, session):
		"""
		Build base query with localization JOINs for name and hint

		:param session:
			Database session
		:return:
			Tuple of (query, NameLocalization alias, HintLocalization alias)
		"""
		NameLocalization = aliased(LocalizationMapper)
		HintLocalization = aliased(LocalizationMapper)

		query = session.query(
			ItemMapper,
			NameLocalization.text.label('loc_name'),
			HintLocalization.text.label('loc_hint')
		).join(
			NameLocalization,
			NameLocalization.kb_id == func.concat('itm_', ItemMapper.kb_id, '_name')
		).outerjoin(
			HintLocalization,
			HintLocalization.kb_id == func.concat('itm_', ItemMapper.kb_id, '_hint')
		)

		return query, NameLocalization, HintLocalization

	def _row_to_entity(self, row: tuple) -> Item:
		"""
		Convert query row with localization to Item entity

		:param row:
			Tuple of (ItemMapper, name_text, hint_text)
		:return:
			Item entity
		:raises LocalizationNotFoundException:
			When name localization is missing
		"""
		mapper, name, hint = row

		if not name:
			raise LocalizationNotFoundException(
				entity_type="Item",
				kb_id=mapper.kb_id,
				localization_key=f"itm_{mapper.kb_id}_name"
			)

		propbits_enum = None
		if mapper.propbits is not None:
			propbits_enum = self._convert_propbits_to_enum(mapper.propbits)

		return Item(
			id=mapper.id,
			item_set_id=mapper.item_set_id,
			kb_id=mapper.kb_id,
			name=name,
			price=mapper.price,
			hint=hint,
			propbits=propbits_enum,
			tiers=mapper.tiers,
			level=mapper.level
		)

	def create(self, item: Item) -> Item:
		"""
		Create new item

		:param item:
			Item entity to create
		:return:
			Created item with database ID
		"""
		return self._create_single(item)

	def get_by_id(self, item_id: int) -> Item | None:
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			row = query.filter(ItemMapper.id == item_id).first()
			return self._row_to_entity(row) if row else None

	def get_by_kb_id(self, kb_id: str) -> Item | None:
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			row = query.filter(ItemMapper.kb_id == kb_id).first()
			return self._row_to_entity(row) if row else None

	def list_all(self, sort_by: str = "name", sort_order: str = "asc") -> list[Item]:
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			query = self._apply_sorting_with_localization(query, sort_by, sort_order)
			rows = query.all()
			return [self._row_to_entity(row) for row in rows]

	def search_by_name(self, query: str) -> list[Item]:
		with self._get_session() as session:
			base_query, NameLocalization, *_ = self._build_query_with_localization(session)
			rows = base_query.filter(
				NameLocalization.text.ilike(f"%{query}%")
			).all()
			return [self._row_to_entity(row) for row in rows]

	def create_batch(self, items: list[Item]) -> list[Item]:
		"""
		Create multiple items

		:param items:
			List of item entities to create
		:return:
			List of created items with database IDs
		"""
		return self._create_batch(items)


	def get_by_kb_ids(self, kb_ids: list[str]) -> dict[str, Item]:
		"""
		Get multiple items by their kb_ids

		:param kb_ids:
			List of kb_id strings
		:return:
			Dictionary mapping kb_id to Item entity
		"""
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			rows = query.filter(ItemMapper.kb_id.in_(kb_ids)).all()

			result = {}
			for row in rows:
				item = self._row_to_entity(row)
				result[item.kb_id] = item

			return result


	def list_by_item_set_id(self, item_set_id: int) -> list[Item]:
		"""
		Get all items belonging to a specific item set

		:param item_set_id:
			Item set ID
		:return:
			List of items in the set
		"""
		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			rows = query.filter(ItemMapper.item_set_id == item_set_id).all()
			return [self._row_to_entity(row) for row in rows]

	def search_with_filters(
		self,
		name_query: str | None = None,
		level: int | None = None,
		hint_regex: str | None = None,
		propbit: str | None = None,
		item_set_id: int | None = None,
		item_id: int | None = None,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Item]:
		"""
		Search items with multiple filter criteria using AND logic

		:param name_query:
			Optional name search (case-insensitive LIKE)
		:param level:
			Optional level filter (exact match)
		:param hint_regex:
			Optional PostgreSQL regex pattern for hint field
		:param propbit:
			Optional propbit value (matches if ANY propbit matches)
		:param item_set_id:
			Optional item set ID filter
		:param item_id:
			Optional item ID filter (exact match)
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of items matching all provided criteria
		"""
		with self._get_session() as session:
			query, NameLocalization, HintLocalization = self._build_query_with_localization(session)

			if item_id is not None:
				query = query.filter(ItemMapper.id == item_id)

			if name_query:
				query = query.filter(NameLocalization.text.ilike(f"%{name_query}%"))

			if level is not None:
				query = query.filter(ItemMapper.level == level)

			if hint_regex:
				query = query.filter(HintLocalization.text.op('~*')(hint_regex))

			if propbit:
				query = query.filter(ItemMapper.propbits.any(propbit))

			if item_set_id is not None:
				query = query.filter(ItemMapper.item_set_id == item_set_id)

			query = self._apply_sorting_with_localization(query, sort_by, sort_order)

			rows = query.all()
			return [self._row_to_entity(row) for row in rows]

	def _apply_sorting_with_localization(self, query, sort_by: str, sort_order: str):
		"""
		Apply ORDER BY clause to query with localization

		:param query:
			SQLAlchemy query with localization joins
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		from sqlalchemy import desc, asc, text

		if sort_by == "name":
			sort_column = text('loc_name')
		elif sort_by == "price":
			sort_column = ItemMapper.price
		elif sort_by == "level":
			sort_column = ItemMapper.level
		else:
			sort_column = text('loc_name')

		if sort_order.lower() == "desc":
			return query.order_by(desc(sort_column))
		else:
			return query.order_by(asc(sort_column))

	def get_distinct_levels(self) -> list[int]:
		"""
		Get list of distinct level values

		:return:
			Sorted list of distinct levels
		"""
		with self._get_session() as session:
			levels = session.query(ItemMapper.level).distinct().order_by(ItemMapper.level).all()
			return [level[0] for level in levels]

	def get_by_ids(self, ids: list[int]) -> dict[int, Item]:
		"""
		Batch fetch items by IDs

		:param ids:
			List of item IDs
		:return:
			Dictionary mapping ID to Item
		"""
		if not ids:
			return {}

		with self._get_session() as session:
			query, *_ = self._build_query_with_localization(session)
			rows = query.filter(ItemMapper.id.in_(ids)).all()

			result = {}
			for row in rows:
				item = self._row_to_entity(row)
				result[item.id] = item

			return result

	def _convert_propbits_to_enum(self, propbits: list[str]) -> list[Propbit]:
		"""
		Convert list of propbit strings to Propbit enums

		:param propbits:
			List of propbit string values from database
		:return:
			List of Propbit enum values
		:raises InvalidPropbitException:
			When any propbit value is invalid
		"""
		result = []
		valid_values = [pb.value for pb in Propbit]

		for propbit_str in propbits:
			try:
				result.append(Propbit(propbit_str))
			except ValueError as e:
				raise InvalidPropbitException(
					invalid_value=propbit_str,
					valid_values=valid_values,
					original_exception=e
				)

		return result

	def _convert_propbits_to_strings(self, propbits: list[Propbit]) -> list[str]:
		"""
		Convert list of Propbit enums to strings for database

		:param propbits:
			List of Propbit enum values
		:return:
			List of string values
		"""
		return [pb.value for pb in propbits]

	def _mapper_to_entity(self, mapper: ItemMapper) -> Item:
		"""
		Convert ItemMapper to Item entity

		Note: This method is called after creating entities. Since name/hint
		are stored in localization table, we fetch the full entity with localization.

		:param mapper:
			ItemMapper to convert
		:return:
			Item entity with localized name and hint
		"""
		return self.get_by_id(mapper.id)

