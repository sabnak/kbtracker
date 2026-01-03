from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.game.repositories.mappers.base import Base


class SpellMapper(Base):

	__tablename__ = "spell"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False, unique=True)
	profit = Column(Integer, nullable=False)
	price = Column(Integer, nullable=False)
	school = Column(Integer, nullable=False)
	mana_cost = Column(ARRAY(Integer), nullable=True)
	crystal_cost = Column(ARRAY(Integer), nullable=True)
	data = Column(JSONB, nullable=False)
	loc = Column(JSONB, nullable=True)
