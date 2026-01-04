from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ShopInventoryMapper(Base):
	__tablename__ = "shop_inventory"

	entity_id = Column(Integer, primary_key=True)
	shop_id = Column(Integer, ForeignKey("shop.id"), primary_key=True)
	profile_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
	type = Column(String(20), primary_key=True, nullable=False)
	count = Column(Integer, nullable=False, default=1)

	shop = relationship("ShopMapper", back_populates="inventory")
	profile = relationship("ProfileMapper", back_populates="shop_inventory")
