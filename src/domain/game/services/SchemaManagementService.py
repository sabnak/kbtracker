from dependency_injector.wiring import Provide
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from src.core.Container import Container
from src.domain.game.ISchemaManagementService import ISchemaManagementService


class SchemaManagementService(ISchemaManagementService):

	def __init__(
		self,
		session_factory: sessionmaker[Session] = Provide[Container.db_session_factory]
	):
		self._session_factory = session_factory

	def get_schema_name(self, game_id: int) -> str:
		"""
		Get schema name for a game ID

		:param game_id:
			Game ID
		:return:
			Schema name (e.g., game_1)
		"""
		return f"game_{game_id}"

	def create_game_schema(self, game_id: int) -> None:
		"""
		Create a new PostgreSQL schema for the game with all required tables

		:param game_id:
			Game ID to create schema for
		:return:
		"""
		schema_name = self.get_schema_name(game_id)

		with self._session_factory() as session:
			# Create schema
			session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

			# Create profile table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.profile (
					id SERIAL PRIMARY KEY,
					name VARCHAR(255) NOT NULL,
					hash VARCHAR(32),
					full_name VARCHAR(255),
					save_dir VARCHAR(255),
					created_at TIMESTAMP DEFAULT NOW()
				)
			"""))

			# Create item_set table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.item_set (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE
				)
			"""))

			# Create item table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.item (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE,
					price INTEGER DEFAULT 0,
					propbits VARCHAR(255)[],
					tiers VARCHAR(255)[],
					item_set_id INTEGER REFERENCES {schema_name}.item_set(id),
					level INTEGER DEFAULT 1
				)
			"""))

			# Create atom_map table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.atom_map (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE
				)
			"""))

			# Create localization table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.localization (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE,
					text TEXT NOT NULL,
					source VARCHAR(255),
					tag VARCHAR(255)
				)
			"""))

			# Create unit table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.unit (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE,
					name VARCHAR(255) NOT NULL,
					unit_class VARCHAR(50) NOT NULL,
					main JSONB NOT NULL,
					params JSONB NOT NULL,
					cost INTEGER,
					krit INTEGER,
					race VARCHAR(100),
					level INTEGER,
					speed INTEGER,
					attack INTEGER,
					defense INTEGER,
					hitback INTEGER,
					hitpoint INTEGER,
					movetype INTEGER,
					defenseup INTEGER,
					initiative INTEGER,
					leadership INTEGER,
					resistance JSONB,
					features JSONB,
					attacks JSONB
				)
			"""))

			# Create spell table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.spell (
					id SERIAL PRIMARY KEY,
					kb_id VARCHAR(255) NOT NULL UNIQUE,
					profit INTEGER NOT NULL,
					price INTEGER NOT NULL,
					school INTEGER NOT NULL,
					hide INTEGER NOT NULL DEFAULT 0,
					mana_cost INTEGER[],
					crystal_cost INTEGER[],
					data JSONB NOT NULL
				)
			"""))

			# Create shop_inventory table
			session.execute(text(f"""
				CREATE TABLE {schema_name}.shop_inventory (
					entity_id INTEGER NOT NULL,
					atom_map_id INTEGER REFERENCES {schema_name}.atom_map(id),
					profile_id INTEGER REFERENCES {schema_name}.profile(id),
					type VARCHAR(20) NOT NULL,
					count INTEGER DEFAULT 1,
					PRIMARY KEY (entity_id, atom_map_id, profile_id, type)
				)
			"""))

			session.commit()

	def delete_game_schema(self, game_id: int) -> None:
		"""
		Delete the PostgreSQL schema for the game (drops all tables and data)

		:param game_id:
			Game ID to delete schema for
		:return:
		"""
		schema_name = self.get_schema_name(game_id)

		with self._session_factory() as session:
			session.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
			session.commit()

	def recreate_game_schema(self, game_id: int) -> None:
		"""
		Recreate game schema by dropping all tables and recreating them

		:param game_id:
			Game ID to recreate schema for
		:return:
		"""
		schema_name = self.get_schema_name(game_id)

		# Drop all tables in the schema
		self._drop_all_tables_in_schema(schema_name)

		# Recreate all tables (create_game_schema uses IF NOT EXISTS for schema)
		self.create_game_schema(game_id)

	def _drop_all_tables_in_schema(self, schema_name: str) -> None:
		"""
		Drop all tables in a schema

		:param schema_name:
			Schema name to drop tables from
		:return:
		"""
		with self._session_factory() as session:
			# Get all table names in the schema
			result = session.execute(text("""
				SELECT tablename
				FROM pg_tables
				WHERE schemaname = :schema_name
			"""), {"schema_name": schema_name})

			table_names = [row[0] for row in result]

			# Drop all tables with CASCADE
			# CASCADE handles foreign key dependencies automatically
			for table_name in table_names:
				session.execute(text(
					f"DROP TABLE IF EXISTS {schema_name}.{table_name} CASCADE"
				))

			session.commit()
