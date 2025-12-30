from sqlalchemy import func
from sqlalchemy.orm import aliased

from src.domain.CrudRepository import CrudRepository
from src.domain.exceptions import LocalizationNotFoundException
from src.domain.game.entities.ItemSet import ItemSet
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.repositories.mappers.ItemSetMapper import ItemSetMapper
from src.domain.game.repositories.mappers.LocalizationMapper import LocalizationMapper


class ItemSetRepository(CrudRepository[ItemSet, ItemSetMapper], IItemSetRepository):

	def _entity_to_mapper(self, entity: ItemSet) -> ItemSetMapper:
		"""
		Convert ItemSet entity to ItemSetMapper

		:param entity:
			ItemSet entity to convert
		:return:
			ItemSetMapper instance
		"""
		return ItemSetMapper(kb_id=entity.kb_id)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "ItemSet"

	def _get_duplicate_identifier(self, entity: ItemSet) -> str:
		"""
		Get duplicate identifier for ItemSet

		:param entity:
			ItemSet entity
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
			SQLAlchemy query with localization joins
		"""
		NameLocalization = aliased(LocalizationMapper)
		HintLocalization = aliased(LocalizationMapper)

		return session.query(
			ItemSetMapper,
			NameLocalization.text.label('loc_name'),
			HintLocalization.text.label('loc_hint')
		).join(
			NameLocalization,
			NameLocalization.kb_id == func.concat('itm_', ItemSetMapper.kb_id, '_name')
		).outerjoin(
			HintLocalization,
			HintLocalization.kb_id == func.concat('itm_', ItemSetMapper.kb_id, '_hint')
		)

	def _row_to_entity(self, row: tuple) -> ItemSet:
		"""
		Convert query row with localization to ItemSet entity

		:param row:
			Tuple of (ItemSetMapper, name_text, hint_text)
		:return:
			ItemSet entity
		:raises LocalizationNotFoundException:
			When name localization is missing
		"""
		mapper, name, hint = row

		if not name:
			raise LocalizationNotFoundException(
				entity_type="ItemSet",
				kb_id=mapper.kb_id,
				localization_key=f"itm_{mapper.kb_id}_name"
			)

		return ItemSet(
			id=mapper.id,
			kb_id=mapper.kb_id,
			name=name,
			hint=hint
		)

	def create(self, item_set: ItemSet) -> ItemSet:
		"""
		Create new item set

		:param item_set:
			Item set entity to create
		:return:
			Created item set with database ID
		"""
		return self._create_single(item_set)

	def get_by_id(self, item_set_id: int) -> ItemSet | None:
		with self._get_session() as session:
			query = self._build_query_with_localization(session)
			row = query.filter(ItemSetMapper.id == item_set_id).first()
			return self._row_to_entity(row) if row else None

	def get_by_kb_id(self, kb_id: str) -> ItemSet | None:
		with self._get_session() as session:
			query = self._build_query_with_localization(session)
			row = query.filter(ItemSetMapper.kb_id == kb_id).first()
			return self._row_to_entity(row) if row else None

	def list_by_ids(self, item_set_ids: list[int]) -> list[ItemSet]:
		"""
		Get multiple item sets by their IDs

		:param item_set_ids:
			List of item set IDs
		:return:
			List of item sets
		"""
		if not item_set_ids:
			return []

		with self._get_session() as session:
			query = self._build_query_with_localization(session)
			rows = query.filter(ItemSetMapper.id.in_(item_set_ids)).all()
			return [self._row_to_entity(row) for row in rows]

	def list_all(self) -> list[ItemSet]:
		with self._get_session() as session:
			query = self._build_query_with_localization(session)
			rows = query.all()
			return [self._row_to_entity(row) for row in rows]

	def create_batch(self, item_sets: list[ItemSet]) -> list[ItemSet]:
		"""
		Create multiple item sets

		:param item_sets:
			List of item set entities to create
		:return:
			List of created item sets with database IDs
		"""
		return self._create_batch(item_sets)

	def _mapper_to_entity(self, mapper: ItemSetMapper) -> ItemSet:
		"""
		Convert ItemSetMapper to ItemSet entity

		Note: This method is called after creating entities. Since name/hint
		are stored in localization table, we fetch the full entity with localization.

		:param mapper:
			ItemSetMapper to convert
		:return:
			ItemSet entity with localized name and hint
		"""
		return self.get_by_id(mapper.id)
