from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IGameService import IGameService
from src.domain.game.entities.Game import Game


class GameService(IGameService):

	def __init__(self, game_repository: IGameRepository = Provide[Container.game_repository]):
		self._game_repository = game_repository

	def create_game(self, name: str, path: str) -> Game:
		"""
		Create new game

		:param name:
			Game display name
		:param path:
			Game path relative to /data directory
		:return:
			Created game
		"""
		game = Game(id=0, name=name, path=path)
		return self._game_repository.create(game)

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
		Delete game (cascades to profiles and game data)

		:param game_id:
			Game ID
		:return:
		"""
		self._game_repository.delete(game_id)
