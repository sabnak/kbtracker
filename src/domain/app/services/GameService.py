from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.app.interfaces.IGameService import IGameService
from src.domain.app.interfaces.ISchemaManagementService import ISchemaManagementService
from src.domain.app.entities.Game import Game


class GameService(IGameService):

	def __init__(
		self,
		game_repository: IGameRepository = Provide[Container.game_repository],
		schema_mgmt: ISchemaManagementService = Provide[Container.schema_management_service]
	):
		self._game_repository = game_repository
		self._schema_mgmt = schema_mgmt

	def create_game(
		self,
		name: str,
		path: str,
		sessions: list[str],
		saves_pattern: str
	) -> Game:
		"""
		Create new game

		:param name:
			Game display name
		:param path:
			Game path relative to /data directory
		:param sessions:
			List of session directories for this game
		:param saves_pattern:
			Resolved pattern for finding save files
		:return:
			Created game
		"""
		game = Game(
			id=0,
			name=name,
			path=path,
			last_scan_time=None,
			sessions=list(set(sessions)),
			saves_pattern=saves_pattern
		)
		game = self._game_repository.create(game)

		# Create schema for new game
		self._schema_mgmt.create_game_schema(game.id)

		return game

	def list_games(self) -> list[Game]:
		"""
		Get all games

		:return:
			List of all games sorted by name
		"""
		return self._game_repository.list_all()

	def get_game(self, game_id: int) -> Game | None:
		"""
		Get game by ID

		:param game_id:
			Game ID
		:return:
			Game or None if not found
		"""
		return self._game_repository.get_by_id(game_id)

	def delete_game(self, game_id: int) -> None:
		"""
		Delete game (drops schema with all tables and data)

		:param game_id:
			Game ID
		:return:
		"""
		# Drop schema (removes all tables and data)
		self._schema_mgmt.delete_game_schema(game_id)

		# Delete game record from public.game table
		self._game_repository.delete(game_id)

	def prepare_rescan(self, game_id: int) -> None:
		"""
		Prepare game for rescan by dropping all tables and recreating schema

		:param game_id:
			Game ID to prepare for rescan
		:return:
		"""
		self._schema_mgmt.recreate_game_schema(game_id)
