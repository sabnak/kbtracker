from sqlalchemy.orm import Session
from src.domain.game.entities.Item import Item
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.repositories.mappers.ItemMapper import ItemMapper


class ItemRepository(IItemRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, item: Item) -> Item:
		mapper = ItemMapper(
			game_id=item.game_id,
			kb_id=item.kb_id,
			name=item.name,
			price=item.price,
			hint=item.hint,
			propbits=item.propbits
		)
		self._session.add(mapper)
		self._session.commit()
		self._session.refresh(mapper)
		return self._mapper_to_entity(mapper)

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
		mappers = [
			ItemMapper(
				game_id=item.game_id,
				kb_id=item.kb_id,
				name=item.name,
				price=item.price,
				hint=item.hint,
				propbits=item.propbits
			)
			for item in items
		]
		self._session.add_all(mappers)
		self._session.commit()
		for mapper in mappers:
			self._session.refresh(mapper)
		return [self._mapper_to_entity(m) for m in mappers]

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

	@staticmethod
	def _mapper_to_entity(mapper: ItemMapper) -> Item:
		return Item(
			id=mapper.id,
			game_id=mapper.game_id,
			kb_id=mapper.kb_id,
			name=mapper.name,
			price=mapper.price,
			hint=mapper.hint,
			propbits=mapper.propbits
		)
