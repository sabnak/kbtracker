from abc import ABC, abstractmethod

from src.domain.app.entities.Game import Game


class IGameRepository(ABC):

	@abstractmethod
	def create(self, game: Game) -> Game:
		"""
		Create new game

		:param game:
			Game to create
		:return:
			Created game with ID
		"""
		pass

	@abstractmethod
	def get_by_id(self, game_id: int) -> Game | None:
		"""
		Get game by ID

		:param game_id:
			Game ID
		:return:
			Game or None if not found
		"""
		pass

	@abstractmethod
	def get_by_path(self, path: str) -> Game | None:
		"""
		Get game by path

		:param path:
			Game path
		:return:
			Game or None if not found
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[Game]:
		"""
		Get all games

		:return:
			List of all games sorted by name
		"""
		pass

	@abstractmethod
	def delete(self, game_id: int) -> None:
		"""
		Delete game

		:param game_id:
			Game ID
		:return:
		"""
		pass
