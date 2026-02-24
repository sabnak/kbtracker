import abc

from src.domain.app.entities.Game import Game


class IKFSExtractor(abc.ABC):

	@abc.abstractmethod
	def extract_archives(self, game: Game) -> str:
		"""
		Extract all game archives to /tmp/<game.path>/

		Data archives go to /tmp/<game.path>/data/
		Localization archives go to /tmp/<game.path>/loc/

		:param game:
			Game entity with path and sessions list
		:return:
			Path to extraction root (/tmp/<game.path>/)
		"""
		...
