from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class LocationMapper(Base):
	__tablename__ = "location"

	id = Column(Integer, primary_key=True, autoincrement=True)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	kb_id = Column(String, nullable=False, index=True)
	name = Column(String, nullable=False)

	game = relationship("GameMapper", back_populates="locations")
	shops = relationship("ShopMapper", back_populates="location")
