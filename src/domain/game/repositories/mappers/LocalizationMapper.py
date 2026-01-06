from sqlalchemy import Column, Integer, String, Text

from src.domain.base.repositories.mappers.base import Base


class LocalizationMapper(Base):
	__tablename__ = "localization"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False, unique=True)
	text = Column(Text, nullable=False)
	source = Column(String(255), nullable=True)
	tag = Column(String(255), nullable=True)
