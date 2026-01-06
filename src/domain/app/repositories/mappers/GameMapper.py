from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, DateTime

from src.domain.base.repositories.mappers.base import Base


class GameMapper(Base):
	__tablename__ = "game"
	__table_args__ = {"schema": "public"}

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	path = Column(String(100), nullable=False, unique=True, index=True)
	last_scan_time = Column(DateTime, nullable=True, default=None)
