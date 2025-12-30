from abc import ABC, abstractmethod


class ISchemaManagementService(ABC):

	@abstractmethod
	def create_game_schema(self, game_id: int) -> None:
		"""
		Create a new PostgreSQL schema for the game

		:param game_id:
			Game ID to create schema for
		:return:
		"""
		pass

	@abstractmethod
	def delete_game_schema(self, game_id: int) -> None:
		"""
		Delete the PostgreSQL schema for the game

		:param game_id:
			Game ID to delete schema for
		:return:
		"""
		pass

	@abstractmethod
	def get_schema_name(self, game_id: int) -> str:
		"""
		Get schema name for a game ID

		:param game_id:
			Game ID
		:return:
			Schema name (e.g., game_1)
		"""
		pass
