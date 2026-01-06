from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.base.repositories.mappers.base import Base


class MetaMapper(Base):
	__tablename__ = "meta"
	__table_args__ = {"schema": "public"}

	name = Column(String(255), nullable=False)
	value = Column(JSONB, nullable=True)
