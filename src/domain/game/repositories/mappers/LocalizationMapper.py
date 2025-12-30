from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, Index, ForeignKey
from sqlalchemy.orm import relationship

from src.domain.game.repositories.mappers.base import Base


class LocalizationMapper(Base):
	__tablename__ = "localization"

	id = Column(Integer, primary_key=True, autoincrement=True)
	game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
	kb_id = Column(String(255), nullable=False)
	text = Column(Text, nullable=False)
	source = Column(String(255), nullable=True)
	tag = Column(String(255), nullable=True)

	game = relationship("GameMapper", back_populates="localizations")

	__table_args__ = (
		UniqueConstraint('game_id', 'kb_id', name='uq_localization_game_id_kb_id'),
		Index('ix_localization_kb_id', 'kb_id'),
		Index('ix_localization_game_id', 'game_id'),
	)
