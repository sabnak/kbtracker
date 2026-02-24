from sqlalchemy import Column, Integer, String

from src.domain.base.repositories.mappers.base import Base


class EntityMapper(Base):
	__abstract__ = True

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, unique=True)
