from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.ItemSet import ItemSet
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.repositories.mappers.ItemSetMapper import ItemSetMapper


class ItemSetRepository(CrudRepository[ItemSet, ItemSetMapper], IItemSetRepository):

	def _entity_to_mapper(self, entity: ItemSet) -> ItemSetMapper:
		"""
		Convert ItemSet entity to ItemSetMapper

		:param entity:
			ItemSet entity to convert
		:return:
			ItemSetMapper instance
		"""
		return ItemSetMapper(
			kb_id=entity.kb_id,
			name=entity.name,
			hint=entity.hint
		)

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
			mapper = session.query(ItemSetMapper).filter(
				ItemSetMapper.id == item_set_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> ItemSet | None:
		with self._get_session() as session:
			mapper = session.query(ItemSetMapper).filter(
				ItemSetMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

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
			mappers = session.query(ItemSetMapper).filter(
				ItemSetMapper.id.in_(item_set_ids)
			).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def list_all(self) -> list[ItemSet]:
		with self._get_session() as session:
			mappers = session.query(ItemSetMapper).all()
			return [self._mapper_to_entity(m) for m in mappers]

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
		return ItemSet(
			id=mapper.id,
			kb_id=mapper.kb_id,
			name=mapper.name,
			hint=mapper.hint
		)
