from sqlalchemy import Column, Integer, String

from src.domain.base.repositories.mappers.base import Base


class AtomMapMapper(Base):
	__tablename__ = "atom_map"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String, nullable=False, unique=True)
