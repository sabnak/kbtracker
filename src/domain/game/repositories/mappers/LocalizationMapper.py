from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, Index

from src.domain.game.repositories.mappers.base import Base


class LocalizationMapper(Base):
	__tablename__ = "localization"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False)
	text = Column(Text, nullable=False)
	source = Column(String(255), nullable=True)
	tag = Column(String(255), nullable=True)

	__table_args__ = (
		UniqueConstraint('kb_id', name='uq_localization_kb_id'),
		Index('ix_localization_kb_id', 'kb_id'),
	)
