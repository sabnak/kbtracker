from sqlalchemy import Column, Integer, String, JSON

from src.domain.base.repositories.mappers.base import Base


class MetaMapper(Base):
	__tablename__ = "meta"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False, unique=True)
	value = Column(JSON, nullable=False)
