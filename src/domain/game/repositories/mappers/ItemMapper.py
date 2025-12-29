from sqlalchemy import Column, Integer, String, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ItemMapper(Base):
	__tablename__ = "item"

	id = Column(Integer, primary_key=True, autoincrement=True)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	kb_id = Column(String, nullable=False, index=True)
	name = Column(String, nullable=False)
	price = Column(Integer, nullable=False, default=0)
	hint = Column(Text, nullable=True)
	propbits = Column(ARRAY(String), nullable=True)
	item_set_id = Column(Integer, ForeignKey("item_set.id"), nullable=True)
	level = Column(Integer, nullable=False, default=1)

	game = relationship("GameMapper", back_populates="items")
	shop_items = relationship("ShopHasItemMapper", back_populates="item")
	item_set = relationship("ItemSetMapper")
