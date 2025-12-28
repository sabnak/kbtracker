from sqlalchemy import Column, Integer, String, Text, ARRAY
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ItemMapper(Base):
	__tablename__ = "item"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, unique=True, nullable=False, index=True)
	name = Column(String, nullable=False)
	price = Column(Integer, nullable=False, default=0)
	hint = Column(Text, nullable=True)
	propbits = Column(ARRAY(String), nullable=True)

	object_items = relationship("ObjectHasItemMapper", back_populates="item")
