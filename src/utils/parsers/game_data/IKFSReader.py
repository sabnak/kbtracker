import abc


class IKFSReader(abc.ABC):

	@abc.abstractmethod
	def read_data_files(
		self,
		game_name: str,
		patterns: list[str],
		encoding: str = 'utf-16-le'
	) -> list[str]:
		"""
		Read data files from extracted data directory

		Supports glob patterns for dynamic file discovery.

		:param game_name:
			Game name (builds path as /tmp/<game_name>/data/)
		:param patterns:
			List of filenames or glob patterns (e.g., ['items*.txt', 'spells.txt'])
		:param encoding:
			Text encoding (default: utf-16-le)
		:return:
			List of file contents as strings
		:raises FileNotFoundError:
			If no files match pattern or directory not found
		"""
		...

	@abc.abstractmethod
	def read_loc_files(
		self,
		game_name: str,
		patterns: list[str],
		encoding: str = 'utf-16-le'
	) -> list[str]:
		"""
		Read localization files from extracted loc directory

		Supports glob patterns for dynamic file discovery.

		:param game_name:
			Game name (builds path as /tmp/<game_name>/loc/)
		:param patterns:
			List of filenames or glob patterns (e.g., ['rus_*.lng', 'eng_items.lng'])
		:param encoding:
			Text encoding (default: utf-16-le)
		:return:
			List of file contents as strings
		:raises FileNotFoundError:
			If no files match pattern or directory not found
		"""
		...
