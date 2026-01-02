from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.game.repositories.mappers.base import Base


class UnitMapper(Base):
	__tablename__ = "unit"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False, unique=True)
	unit_class = Column(String(50), nullable=False)
	params = Column(JSONB, nullable=False)
	main = Column(JSONB, nullable=False)
