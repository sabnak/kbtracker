from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.base import Base


class SpellMapper(Base):

	__tablename__ = "spell"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False, unique=True)
	profit = Column(Integer, nullable=False)
	price = Column(Integer, nullable=False)
	school = Column(Integer, nullable=False)
	hide = Column(Integer, nullable=False, default=0)
	mana_cost = Column(ARRAY(Integer), nullable=True)
	crystal_cost = Column(ARRAY(Integer), nullable=True)
	data = Column(JSONB, nullable=False)

	shop_inventory = relationship(
		"ShopInventoryMapper",
		foreign_keys="[ShopInventoryMapper.entity_id]",
		primaryjoin="and_(SpellMapper.id == ShopInventoryMapper.entity_id, ShopInventoryMapper.type == 'spell')",
		viewonly=True
	)
