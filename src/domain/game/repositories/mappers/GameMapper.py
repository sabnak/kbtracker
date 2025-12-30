from sqlalchemy import Column, Integer, String

from src.domain.game.repositories.mappers.base import Base


class GameMapper(Base):
	__tablename__ = "game"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	path = Column(String(100), nullable=False, unique=True, index=True)
