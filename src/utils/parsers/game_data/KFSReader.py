import os

from src.utils.parsers.game_data.IKFSReader import IKFSReader


class KFSReader(IKFSReader):

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
		extraction_root = f'/tmp/{game_name}'
		results = []

		for file_path in file_paths:
			content = self._read_file(extraction_root, file_path, encoding)
			results.append(content)

		return results

	def _read_file(
		self,
		extraction_root: str,
		file_path: str,
		encoding: str
	) -> str:
		"""
		Read single file from extraction directory

		:param extraction_root:
			Root extraction directory
		:param file_path:
			File path relative to extraction root
		:param encoding:
			Text encoding
		:return:
			File content as string
		:raises FileNotFoundError:
			If file not found
		"""
		full_path = os.path.join(extraction_root, file_path)

		if not os.path.exists(full_path):
			raise FileNotFoundError(
				f"File '{file_path}' not found in extraction directory '{extraction_root}'"
			)

		with open(full_path, 'rb') as file:
			content_bytes = file.read()

		return self._decode_content(content_bytes, encoding)

	def _decode_content(self, content: bytes, encoding: str) -> str:
		"""
		Decode file content with proper encoding

		Tries specified encoding first, then falls back to UTF-8 if that fails.

		:param content:
			Raw file content as bytes
		:param encoding:
			Primary encoding to try
		:return:
			Decoded string
		:raises UnicodeDecodeError:
			If content cannot be decoded with either encoding
		"""
		try:
			return content.decode(encoding)
		except UnicodeDecodeError:
			try:
				return content.decode('utf-8')
			except UnicodeDecodeError as e:
				raise UnicodeDecodeError(
					e.encoding,
					e.object,
					e.start,
					e.end,
					f"Failed to decode content with {encoding} or UTF-8"
				) from e
