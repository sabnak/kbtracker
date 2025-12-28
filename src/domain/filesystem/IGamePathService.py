from abc import ABC, abstractmethod


class IGamePathService(ABC):

	@abstractmethod
	def get_available_game_paths(self) -> list[str]:
		"""
		Get list of available game paths from data directory

		:return:
			List of directory names, empty if none found or error
		"""
		pass
