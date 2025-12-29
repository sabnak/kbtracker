from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.domain.game.repositories.mappers.base import Base


class ItemSetMapper(Base):
	__tablename__ = "item_set"

	id = Column(Integer, primary_key=True, autoincrement=True)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	kb_id = Column(String, nullable=False, index=True)
	name = Column(String, nullable=False)
	hint = Column(Text, nullable=True)

	game = relationship("GameMapper", back_populates="item_sets")
