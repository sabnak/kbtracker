from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.domain.base.repositories.mappers.base import Base
from src.domain.game.entities.ShopProductType import ShopProductType


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
		foreign_keys="[ShopInventoryMapper.product_id]",
		primaryjoin=f"and_(SpellMapper.id == ShopInventoryMapper.product_id, ShopInventoryMapper.product_type == '{ShopProductType.SPELL.value}')",
		viewonly=True
	)
