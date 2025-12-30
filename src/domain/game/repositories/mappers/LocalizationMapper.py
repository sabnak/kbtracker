from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, Index

from src.domain.game.repositories.mappers.base import Base


class LocalizationMapper(Base):
	__tablename__ = "localization"

	id = Column(Integer, primary_key=True, autoincrement=True)
	kb_id = Column(String(255), nullable=False)
	text = Column(Text, nullable=False)
	type = Column(String(100), nullable=False)

	__table_args__ = (
		UniqueConstraint('kb_id', 'type', name='uq_localization_kb_id_type'),
		Index('ix_localization_kb_id_type', 'kb_id', 'type'),
	)
