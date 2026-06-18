import abc

from src.domain.app.entities.Game import Game


class IGameDataExtractor(abc.ABC):

	@abc.abstractmethod
	def extract(self, game: Game) -> str:
		"""
		Prepare a flat copy of all game data under /tmp/game_<game.id>/

		Combines two sources into a single flat structure:
		archives (delegated to the KFS extractor) and loose, unpacked
		session files copied straight from disk.

		:param game:
			Game entity with path and sessions list
		:return:
			Path to extraction root (/tmp/game_<game.id>/)
		"""
		...

	@abc.abstractmethod
	def cleanup(self, game: Game) -> None:
		"""
		Clean up temporary extracted files for the given game

		:param game:
			Game entity to clean up temporary files for
		"""
		...
