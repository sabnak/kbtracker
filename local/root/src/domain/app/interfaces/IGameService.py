from abc import ABC, abstractmethod

from src.domain.app.entities.Game import Game


class IGameService(ABC):

	@abstractmethod
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
		pass

	@abstractmethod
	def list_games(self) -> list[Game]:
		"""
		Get all games

		:return:
			List of all games sorted by name
		"""
		pass

	@abstractmethod
	def get_game(self, game_id: int) -> Game | None:
		"""
		Get game by ID

		:param game_id:
			Game ID
		:return:
			Game or None if not found
		"""
		pass

	@abstractmethod
	def delete_game(self, game_id: int) -> None:
		"""
		Delete game (cascades to profiles and game data)

		:param game_id:
			Game ID
		:return:
		"""
		pass
