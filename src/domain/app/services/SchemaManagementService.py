from src.domain.app.interfaces.ISchemaManagementService import ISchemaManagementService
from src.utils.db import get_game_database_registry


class SchemaManagementService(ISchemaManagementService):

	def get_schema_name(self, game_id: int) -> str:
		"""
		Get schema name for a game ID

		:param game_id:
			Game ID
		:return:
			Schema name (e.g., game_1), used as the game's database file name
		"""
		return f"game_{game_id}"

	def create_game_schema(self, game_id: int) -> None:
		"""
		Create the game's database file with all required tables

		:param game_id:
			Game ID to create the database for
		:return:
		"""
		get_game_database_registry().ensure_database(self.get_schema_name(game_id))

	def delete_game_schema(self, game_id: int) -> None:
		"""
		Delete the game's database file (drops all tables and data)

		:param game_id:
			Game ID to delete the database for
		:return:
		"""
		get_game_database_registry().drop(self.get_schema_name(game_id))

	def recreate_game_schema(self, game_id: int) -> None:
		"""
		Recreate the game's database by deleting and recreating all tables

		:param game_id:
			Game ID to recreate the database for
		:return:
		"""
		registry = get_game_database_registry()
		schema_name = self.get_schema_name(game_id)
		registry.drop(schema_name)
		registry.ensure_database(schema_name)
