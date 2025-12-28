from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ObjectMapper(Base):
	__tablename__ = "objects"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(Integer, unique=True, nullable=False, index=True)
	location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
	name = Column(String, nullable=False)
	hint = Column(Text, nullable=True)
	msg = Column(Text, nullable=True)

	location = relationship("LocationMapper", back_populates="objects")
	object_items = relationship("ObjectHasItemMapper", back_populates="object")
