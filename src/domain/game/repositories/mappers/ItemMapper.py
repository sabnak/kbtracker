from sqlalchemy import Column, Integer, String, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ItemMapper(Base):
	__tablename__ = "item"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, unique=True)
	price = Column(Integer, nullable=False, default=0)
	propbits = Column(ARRAY(String), nullable=True)
	tiers = Column(ARRAY(String), nullable=True)
	item_set_id = Column(Integer, ForeignKey("item_set.id"), nullable=True)
	level = Column(Integer, nullable=False, default=1)

	shop_inventory = relationship(
		"ShopInventoryMapper",
		foreign_keys="[ShopInventoryMapper.entity_id]",
		primaryjoin="and_(ItemMapper.id == ShopInventoryMapper.entity_id, ShopInventoryMapper.type == 'item')",
		viewonly=True
	)
	item_set = relationship("ItemSetMapper")
