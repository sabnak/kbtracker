from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.domain.base.repositories.mappers.base import Base
from src.domain.game.entities.ShopProductType import ShopProductType


class UnitMapper(Base):
	__tablename__ = "unit"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False, unique=True)
	name = Column(String(255), nullable=False)
	unit_class = Column(String(50), nullable=False)
	params = Column(JSONB, nullable=False)
	main = Column(JSONB, nullable=False)
	cost = Column(Integer, nullable=True)
	krit = Column(Integer, nullable=True)
	race = Column(String(100), nullable=True)
	level = Column(Integer, nullable=True)
	speed = Column(Integer, nullable=True)
	attack = Column(Integer, nullable=True)
	defense = Column(Integer, nullable=True)
	hitback = Column(Integer, nullable=True)
	hitpoint = Column(Integer, nullable=True)
	movetype = Column(Integer, nullable=True)
	defenseup = Column(Integer, nullable=True)
	initiative = Column(Integer, nullable=True)
	leadership = Column(Integer, nullable=True)
	resistance = Column(JSONB, nullable=True)
	features = Column(JSONB, nullable=True)
	attacks = Column(JSONB, nullable=True)

	shop_inventory_sale = relationship(
		"ShopInventoryMapper",
		foreign_keys="[ShopInventoryMapper.product_id]",
		primaryjoin=f"and_(UnitMapper.id == ShopInventoryMapper.product_id, ShopInventoryMapper.product_type == '{ShopProductType.UNIT.value}')",
		viewonly=True
	)

	shop_inventory_garrison = relationship(
		"ShopInventoryMapper",
		foreign_keys="[ShopInventoryMapper.product_id]",
		primaryjoin=f"and_(UnitMapper.id == ShopInventoryMapper.product_id, ShopInventoryMapper.product_type == '{ShopProductType.GARRISON.value}')",
		viewonly=True
	)
