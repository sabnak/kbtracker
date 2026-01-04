from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.base import Base


class ProfileMapper(Base):
	__tablename__ = "profile"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, nullable=False)
	hash = Column(String(32), nullable=True)
	full_name = Column(String(255), nullable=True)
	save_dir = Column(String(255), nullable=True)
	created_at = Column(DateTime, nullable=False, default=datetime.now())

	shop_inventory = relationship("ShopInventoryMapper", back_populates="profile")