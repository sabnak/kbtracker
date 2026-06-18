import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from src.domain.base.repositories.mappers.base import Base

# Tables that live in the shared application database (app.db).
# Every other mapped table is game-specific and lives in a per-game database file.
_APP_TABLE_NAMES: set[str] = {"game", "meta"}


def create_db_engine(database_url: str) -> Engine:
	"""
	Create database engine

	:param database_url:
		Database connection URL
	:return:
		SQLAlchemy engine
	"""
	engine = create_engine(database_url, echo=False)
	if engine.dialect.name == "sqlite":
		_enable_sqlite_pragmas(engine)
	return engine


def _enable_sqlite_pragmas(engine: Engine) -> None:
	"""
	Apply per-connection SQLite pragmas

	- ``foreign_keys=ON``: SQLite does not enforce foreign keys unless this is
	  set per connection. Required for the ``ON DELETE CASCADE`` behaviour of
	  the shop_inventory and hero_inventory tables.
	- ``journal_mode=WAL`` + ``synchronous=NORMAL``: write-ahead logging avoids
	  an fsync on every commit, which is the dominant cost when scanning writes
	  many rows in separate transactions. Safe for a single-user local app.
	- ``busy_timeout``: wait instead of failing immediately on a locked database.

	:param engine:
		SQLite engine to attach the pragma listener to
	:return:
	"""
	@event.listens_for(engine, "connect")
	def _set_sqlite_pragma(dbapi_connection, connection_record):
		cursor = dbapi_connection.cursor()
		cursor.execute("PRAGMA foreign_keys=ON")
		cursor.execute("PRAGMA journal_mode=WAL")
		cursor.execute("PRAGMA synchronous=NORMAL")
		cursor.execute("PRAGMA busy_timeout=5000")
		cursor.close()


def init_db(engine: Engine) -> None:
	"""
	Initialize database and create all tables

	:param engine:
		Database engine
	:return:
	"""
	Base.metadata.create_all(bind=engine)


def get_db_session(session_factory: sessionmaker[Session]) -> Session:
	"""
	Get database session

	:param session_factory:
		Session factory
	:return:
		Database session
	"""
	return session_factory()


def _game_tables() -> list:
	"""
	Get the list of game-specific tables (everything except the app tables)

	:return:
		Tables that belong in a per-game database
	"""
	return [
		table
		for name, table in Base.metadata.tables.items()
		if name not in _APP_TABLE_NAMES
	]


class GameDatabaseRegistry:
	"""
	Lazily creates and caches one SQLite database (engine + session factory)
	per game, stored as ``<data_dir>/<schema_name>.db``
	"""

	def __init__(self, data_dir: str):
		self._data_dir = data_dir
		self._engines: dict[str, Engine] = {}
		self._session_factories: dict[str, sessionmaker[Session]] = {}

	def _db_path(self, schema_name: str) -> str:
		return os.path.join(self._data_dir, f"{schema_name}.db")

	def get_session_factory(self, schema_name: str) -> sessionmaker[Session]:
		"""
		Get (creating on first use) the session factory for a game database

		:param schema_name:
			Game schema name (e.g. game_1), used as the database file name
		:return:
			Session factory bound to the game's database
		"""
		if schema_name not in self._session_factories:
			self._session_factories[schema_name] = self._build(schema_name)
		return self._session_factories[schema_name]

	def ensure_database(self, schema_name: str) -> None:
		"""
		Ensure the game database file exists with all game tables created

		:param schema_name:
			Game schema name
		:return:
		"""
		self.get_session_factory(schema_name)

	def drop(self, schema_name: str) -> None:
		"""
		Dispose the game's engine and delete its database file

		:param schema_name:
			Game schema name
		:return:
		"""
		engine = self._engines.pop(schema_name, None)
		if engine is not None:
			engine.dispose()
		self._session_factories.pop(schema_name, None)

		db_path = self._db_path(schema_name)
		if os.path.exists(db_path):
			os.remove(db_path)

	def _build(self, schema_name: str) -> sessionmaker[Session]:
		os.makedirs(self._data_dir, exist_ok=True)
		engine = create_db_engine(f"sqlite:///{self._db_path(schema_name)}")
		Base.metadata.create_all(bind=engine, tables=_game_tables())
		self._engines[schema_name] = engine
		return sessionmaker(autocommit=False, autoflush=False, bind=engine)


_GAME_DB_REGISTRY: GameDatabaseRegistry | None = None


def configure_game_databases(data_dir: str) -> GameDatabaseRegistry:
	"""
	Configure the process-wide game database registry

	:param data_dir:
		Directory where per-game database files are stored
	:return:
		The configured registry
	"""
	global _GAME_DB_REGISTRY
	_GAME_DB_REGISTRY = GameDatabaseRegistry(data_dir)
	return _GAME_DB_REGISTRY


def get_game_database_registry() -> GameDatabaseRegistry:
	"""
	Get the process-wide game database registry

	:return:
		The configured registry
	:raises RuntimeError:
		When the registry has not been configured yet
	"""
	if _GAME_DB_REGISTRY is None:
		raise RuntimeError("Game database registry is not configured")
	return _GAME_DB_REGISTRY
