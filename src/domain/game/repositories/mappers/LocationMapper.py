from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class LocationMapper(Base):
	__tablename__ = "location"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, unique=True)
	name = Column(String, nullable=False)

	shops = relationship("ShopMapper", back_populates="location")
