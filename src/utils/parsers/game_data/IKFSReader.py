import abc


class IKFSReader(abc.ABC):

	@abc.abstractmethod
	def read_files(
		self,
		game_name: str,
		file_paths: list[str],
		encoding: str = 'utf-16-le'
	) -> list[str]:
		"""
		Read file contents from extracted directories

		:param game_name:
			Game name (builds extraction_root as /tmp/<game_name>/)
		:param file_paths:
			List of file paths in format 'archive_basename/file_path'
			Example: ['loc_ses/rus_items.lng', 'ses/items.txt']
		:param encoding:
			Text encoding (default: utf-16-le)
		:return:
			List of file contents as strings, in same order as file_paths
		:raises FileNotFoundError:
			If any requested file not found
		"""
		...
