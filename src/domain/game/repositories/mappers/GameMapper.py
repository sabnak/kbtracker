from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.base import Base


class GameMapper(Base):
	__tablename__ = "game"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	path = Column(String(100), nullable=False, unique=True, index=True)

	# Relationships (will be fully functional after other mappers are updated)
	profiles = relationship("ProfileMapper", back_populates="game", cascade="all, delete-orphan")
	items = relationship("ItemMapper", back_populates="game", cascade="all, delete-orphan")
	item_sets = relationship("ItemSetMapper", back_populates="game", cascade="all, delete-orphan")
	locations = relationship("LocationMapper", back_populates="game", cascade="all, delete-orphan")
	shops = relationship("ShopMapper", back_populates="game", cascade="all, delete-orphan")
