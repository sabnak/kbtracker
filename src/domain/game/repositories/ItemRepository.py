from sqlalchemy.orm import Session
from src.domain.CrudRepository import CrudRepository
from src.domain.game.entities.Item import Item
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.repositories.mappers.ItemMapper import ItemMapper


class ItemRepository(CrudRepository[Item, ItemMapper], IItemRepository):

	def __init__(self, session: Session):
		super().__init__(session)

	def _entity_to_mapper(self, entity: Item) -> ItemMapper:
		"""
		Convert Item entity to ItemMapper

		:param entity:
			Item entity to convert
		:return:
			ItemMapper instance
		"""
		return ItemMapper(
			game_id=entity.game_id,
			item_set_id=entity.item_set_id,
			kb_id=entity.kb_id,
			name=entity.name,
			price=entity.price,
			hint=entity.hint,
			propbits=entity.propbits,
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
		mapper = self._session.query(ItemMapper).filter(
			ItemMapper.id == item_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Item | None:
		mapper = self._session.query(ItemMapper).filter(
			ItemMapper.kb_id == kb_id
		).first()
		return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[Item]:
		mappers = self._session.query(ItemMapper).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def search_by_name(self, query: str) -> list[Item]:
		mappers = self._session.query(ItemMapper).filter(
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

	def list_by_game_id(self, game_id: int) -> list[Item]:
		mappers = self._session.query(ItemMapper).filter(
			ItemMapper.game_id == game_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def search_by_name_and_game(self, query: str, game_id: int) -> list[Item]:
		mappers = self._session.query(ItemMapper).filter(
			ItemMapper.name.ilike(f"%{query}%"),
			ItemMapper.game_id == game_id
		).all()
		return [self._mapper_to_entity(m) for m in mappers]

	def _mapper_to_entity(self, mapper: ItemMapper) -> Item:
		return Item(
			id=mapper.id,
			game_id=mapper.game_id,
			item_set_id=mapper.item_set_id,
			kb_id=mapper.kb_id,
			name=mapper.name,
			price=mapper.price,
			hint=mapper.hint,
			propbits=mapper.propbits,
			level=mapper.level
		)
