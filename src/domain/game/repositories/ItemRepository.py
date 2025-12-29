from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.Item import Item
from src.domain.game.entities.Propbit import Propbit
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.repositories.mappers.ItemMapper import ItemMapper
from src.domain.exceptions import InvalidPropbitException


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
			game_id=entity.game_id,
			item_set_id=entity.item_set_id,
			kb_id=entity.kb_id,
			name=entity.name,
			price=entity.price,
			hint=entity.hint,
			propbits=propbits_str,
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
		return f"game_id={entity.game_id}, kb_id={entity.kb_id}"

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
		with self._session_factory() as session:
			mapper = session.query(ItemMapper).filter(
				ItemMapper.id == item_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Item | None:
		with self._session_factory() as session:
			mapper = session.query(ItemMapper).filter(
				ItemMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Item]:
		with self._session_factory() as session:
			mappers = session.query(ItemMapper).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def search_by_name(self, query: str) -> list[Item]:
		with self._session_factory() as session:
			mappers = session.query(ItemMapper).filter(
				ItemMapper.name.ilike(f"%{query}%")
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def create_batch(self, items: list[Item]) -> list[Item]:
		"""
		Create multiple items

		:param items:
			List of item entities to create
		:return:
			List of created items with database IDs
		"""
		return self._create_batch(items)

	def list_by_game_id(
		self,
		game_id: int,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Item]:
		with self._session_factory() as session:
			query = session.query(ItemMapper).filter(
				ItemMapper.game_id == game_id
			)

			query = self._apply_sorting(query, sort_by, sort_order)

			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def search_by_name_and_game(self, query: str, game_id: int) -> list[Item]:
		with self._session_factory() as session:
			mappers = session.query(ItemMapper).filter(
				ItemMapper.name.ilike(f"%{query}%"),
				ItemMapper.game_id == game_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def list_by_item_set_id(self, item_set_id: int) -> list[Item]:
		"""
		Get all items belonging to a specific item set

		:param item_set_id:
			Item set ID
		:return:
			List of items in the set
		"""
		with self._session_factory() as session:
			mappers = session.query(ItemMapper).filter(
				ItemMapper.item_set_id == item_set_id
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def search_with_filters(
		self,
		game_id: int,
		name_query: str | None = None,
		level: int | None = None,
		hint_regex: str | None = None,
		propbit: str | None = None,
		item_set_id: int | None = None,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Item]:
		"""
		Search items with multiple filter criteria using AND logic

		:param game_id:
			Game ID to filter by
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
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of items matching all provided criteria
		"""
		with self._session_factory() as session:
			query = session.query(ItemMapper).filter(ItemMapper.game_id == game_id)

			if name_query:
				query = query.filter(ItemMapper.name.ilike(f"%{name_query}%"))

			if level is not None:
				query = query.filter(ItemMapper.level == level)

			if hint_regex:
				query = query.filter(ItemMapper.hint.op('~*')(hint_regex))

			if propbit:
				query = query.filter(ItemMapper.propbits.any(propbit))

			if item_set_id is not None:
				query = query.filter(ItemMapper.item_set_id == item_set_id)

			query = self._apply_sorting(query, sort_by, sort_order)

			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def _apply_sorting(self, query, sort_by: str, sort_order: str):
		"""
		Apply ORDER BY clause to SQLAlchemy query

		:param query:
			SQLAlchemy query object
		:param sort_by:
			Field to sort by (name, price, level)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		sort_column = {
			"name": ItemMapper.name,
			"price": ItemMapper.price,
			"level": ItemMapper.level
		}.get(sort_by, ItemMapper.name)

		if sort_order.lower() == "desc":
			return query.order_by(sort_column.desc())
		else:
			return query.order_by(sort_column.asc())

	def get_distinct_levels(self, game_id: int) -> list[int]:
		"""
		Get list of distinct level values for a game

		:param game_id:
			Game ID
		:return:
			Sorted list of distinct levels
		"""
		with self._session_factory() as session:
			levels = session.query(ItemMapper.level).filter(
				ItemMapper.game_id == game_id
			).distinct().order_by(ItemMapper.level).all()
			return [level[0] for level in levels]

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

		:param mapper:
			ItemMapper to convert
		:return:
			Item entity
		:raises InvalidPropbitException:
			When mapper contains invalid propbit values
		"""
		propbits_enum = None
		if mapper.propbits is not None:
			propbits_enum = self._convert_propbits_to_enum(mapper.propbits)

		return Item(
			id=mapper.id,
			game_id=mapper.game_id,
			item_set_id=mapper.item_set_id,
			kb_id=mapper.kb_id,
			name=mapper.name,
			price=mapper.price,
			hint=mapper.hint,
			propbits=propbits_enum,
			level=mapper.level
		)
