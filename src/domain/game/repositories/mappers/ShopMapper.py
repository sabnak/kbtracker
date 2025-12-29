from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ShopMapper(Base):
	__tablename__ = "shop"

	id = Column(Integer, primary_key=True, autoincrement=True)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	kb_id = Column(String, nullable=False, index=True)
	location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
	name = Column(String, nullable=False)
	hint = Column(Text, nullable=True)
	msg = Column(Text, nullable=True)

	game = relationship("GameMapper", back_populates="shops")
	location = relationship("LocationMapper", back_populates="shops")
	shop_items = relationship("ShopHasItemMapper", back_populates="shop")
