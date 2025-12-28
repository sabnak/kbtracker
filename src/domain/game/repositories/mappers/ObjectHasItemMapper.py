from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ObjectHasItemMapper(Base):
	__tablename__ = "objects_has_items"

	item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
	object_id = Column(Integer, ForeignKey("objects.id"), primary_key=True)
	profile_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
	count = Column(Integer, nullable=False, default=1)

	item = relationship("ItemMapper", back_populates="object_items")
	object = relationship("ObjectMapper", back_populates="object_items")
	profile = relationship("ProfileMapper", back_populates="object_items")
