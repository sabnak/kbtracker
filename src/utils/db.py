from sqlalchemy import create_engine, text
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


class SchemaContextSession:
	"""
	Session wrapper that sets search_path to a specific game schema
	"""

	def __init__(self, session: Session, schema_name: str):
		self._session = session
		self._schema_name = schema_name

	def __enter__(self):
		self._session.execute(text(f"SET search_path TO {self._schema_name}"))
		return self._session

	def __exit__(self, exc_type, exc_val, exc_tb):
		self._session.close()


def create_schema_session(
	session_factory: sessionmaker[Session],
	schema_name: str
) -> SchemaContextSession:
	"""
	Create session with search_path set to game schema

	:param session_factory:
		Session factory
	:param schema_name:
		Schema name (e.g., game_1)
	:return:
		Schema context session
	"""
	return SchemaContextSession(session_factory(), schema_name)
