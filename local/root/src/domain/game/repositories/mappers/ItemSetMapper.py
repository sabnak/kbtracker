from sqlalchemy import Column, Integer, String
from src.domain.base.repositories.mappers.base import Base


class ItemSetMapper(Base):
	__tablename__ = "item_set"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, unique=True)
