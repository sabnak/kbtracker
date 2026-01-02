import os
import glob

from src.utils.parsers.game_data.IKFSReader import IKFSReader


class KFSReader(IKFSReader):

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
		data_dir = f'/tmp/{game_name}/data'
		return self._read_files_from_dir(data_dir, patterns, encoding)

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
		loc_dir = f'/tmp/{game_name}/loc'
		return self._read_files_from_dir(loc_dir, patterns, encoding)

	def _read_files_from_dir(
		self,
		directory: str,
		patterns: list[str],
		encoding: str
	) -> list[str]:
		"""
		Read files from specified directory

		Supports glob patterns for dynamic file discovery.

		:param directory:
			Directory path
		:param patterns:
			List of filenames or glob patterns
		:param encoding:
			Text encoding
		:return:
			List of file contents
		:raises FileNotFoundError:
			If directory doesn't exist or no files match patterns
		"""
		# Handle empty patterns list
		if not patterns:
			return []

		if not os.path.exists(directory):
			raise FileNotFoundError(f"Directory not found: {directory}")

		# Expand glob patterns to actual filenames
		filenames = self._expand_patterns(directory, patterns)

		if not filenames:
			raise FileNotFoundError(
				f"No files found matching patterns {patterns} in directory '{directory}'"
			)

		results = []
		for filename in filenames:
			content = self._read_file(directory, filename, encoding)
			results.append(content)

		return results

	def _expand_patterns(self, directory: str, patterns: list[str]) -> list[str]:
		"""
		Expand glob patterns to actual filenames

		:param directory:
			Directory path
		:param patterns:
			List of filenames or glob patterns
		:return:
			Sorted list of unique filenames (basenames only)
		"""
		all_files = set()

		for pattern in patterns:
			# Build full path pattern
			full_pattern = os.path.join(directory, pattern)

			# Expand glob pattern
			matched_paths = glob.glob(full_pattern)

			# Extract basenames and add to set
			for path in matched_paths:
				all_files.add(os.path.basename(path))

		# Return sorted list
		return sorted(all_files)

	def _read_file(
		self,
		directory: str,
		filename: str,
		encoding: str
	) -> str:
		"""
		Read single file from directory

		:param directory:
			Directory path
		:param filename:
			Filename relative to directory
		:param encoding:
			Text encoding
		:return:
			File content as string
		:raises FileNotFoundError:
			If file not found
		"""
		full_path = os.path.join(directory, filename)

		if not os.path.exists(full_path):
			raise FileNotFoundError(
				f"File '{filename}' not found in directory '{directory}'"
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
