from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.models import Base


class ProfileMapper(Base):
	__tablename__ = "profile"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, nullable=False)
	game_version = Column(String, nullable=False)
	created_at = Column(DateTime, nullable=False, default=datetime.now())

	object_items = relationship("ObjectHasItemModel", back_populates="profile")