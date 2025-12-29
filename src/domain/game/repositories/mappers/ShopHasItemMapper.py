from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ShopHasItemMapper(Base):
	__tablename__ = "shops_has_items"

	item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)
	shop_id = Column(Integer, ForeignKey("shop.id"), primary_key=True)
	profile_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
	count = Column(Integer, nullable=False, default=1)

	item = relationship("ItemMapper", back_populates="shop_items")
	shop = relationship("ShopMapper", back_populates="shop_items")
	profile = relationship("ProfileMapper", back_populates="shop_items")
