from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.base.repositories.mappers.base import Base


class MetaMapper(Base):
	__tablename__ = "meta"
	__table_args__ = {"schema": "public"}

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False, unique=True)
	value = Column(JSONB, nullable=False)
