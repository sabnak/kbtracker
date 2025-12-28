from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.domain.game.repositories.mappers.base import Base


def create_db_engine(database_url: str):
	"""
	Create database engine

	:param database_url:
		Database connection URL
	:return:
		SQLAlchemy engine
	"""
	return create_engine(database_url, echo=False)


def create_session_factory(engine):
	"""
	Create session factory

	:param engine:
		SQLAlchemy engine
	:return:
		Session factory
	"""
	return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(database_url: str) -> None:
	"""
	Initialize database and create all tables

	:param database_url:
		Database connection URL
	:return:
	"""
	engine = create_db_engine(database_url)
	Base.metadata.create_all(bind=engine)


def get_db_session(session_factory) -> Session:
	"""
	Get database session

	:param session_factory:
		Session factory
	:return:
		Database session
	"""
	return session_factory()
