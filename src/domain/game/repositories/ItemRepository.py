from sqlalchemy.orm import Session
from src.domain.game.entities.Item import Item
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.repositories.mappers.models import ItemModel


class ItemRepository(IItemRepository):

	def __init__(self, session: Session):
		self._session = session

	def create(self, item: Item) -> Item:
		model = ItemModel(
			kb_id=item.kb_id,
			name=item.name,
			price=item.price,
			hint=item.hint,
			propbits=item.propbits
		)
		self._session.add(model)
		self._session.commit()
		self._session.refresh(model)
		return self._model_to_entity(model)

	def get_by_id(self, item_id: int) -> Item | None:
		model = self._session.query(ItemModel).filter(
			ItemModel.id == item_id
		).first()
		return self._model_to_entity(model) if model else None

	def get_by_kb_id(self, kb_id: str) -> Item | None:
		model = self._session.query(ItemModel).filter(
			ItemModel.kb_id == kb_id
		).first()
		return self._model_to_entity(model) if model else None

	def list_all(self) -> list[Item]:
		models = self._session.query(ItemModel).all()
		return [self._model_to_entity(m) for m in models]

	def search_by_name(self, query: str) -> list[Item]:
		models = self._session.query(ItemModel).filter(
			ItemModel.name.ilike(f"%{query}%")
		).all()
		return [self._model_to_entity(m) for m in models]

	def create_batch(self, items: list[Item]) -> list[Item]:
		models = [
			ItemModel(
				kb_id=item.kb_id,
				name=item.name,
				price=item.price,
				hint=item.hint,
				propbits=item.propbits
			)
			for item in items
		]
		self._session.add_all(models)
		self._session.commit()
		for model in models:
			self._session.refresh(model)
		return [self._model_to_entity(m) for m in models]

	def _model_to_entity(self, model: ItemModel) -> Item:
		return Item(
			id=model.id,
			kb_id=model.kb_id,
			name=model.name,
			price=model.price,
			hint=model.hint,
			propbits=model.propbits
		)
