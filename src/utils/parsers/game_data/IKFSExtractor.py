import abc


class IKFSExtractor(abc.ABC):

	@abc.abstractmethod
	def extract_archives(self, game_name: str) -> str:
		"""
		Extract all game archives to /tmp/<game_name>/

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:return:
			Path to extraction root (/tmp/<game_name>/)
		"""
		...
