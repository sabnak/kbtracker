from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.base import Base


class ProfileMapper(Base):
	__tablename__ = "profile"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, nullable=False)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	created_at = Column(DateTime, nullable=False, default=datetime.now())

	game = relationship("GameMapper", back_populates="profiles")
	shop_items = relationship("ShopHasItemMapper", back_populates="profile")