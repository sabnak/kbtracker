from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.domain.base.repositories.mappers.base import Base


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
		self._original_commit = session.commit

	def __enter__(self):
		self._set_search_path()
		self._session.commit = self._commit_with_schema_reset
		return self._session

	def __exit__(self, exc_type, exc_val, exc_tb):
		self._session.commit = self._original_commit
		self._session.close()

	def _set_search_path(self):
		"""
		Set search_path to game schema
		"""
		self._session.execute(text(f"SET search_path TO {self._schema_name}"))

	def _commit_with_schema_reset(self):
		"""
		Commit and re-set search_path (PostgreSQL resets it after commit)
		"""
		self._original_commit()
		self._set_search_path()


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
