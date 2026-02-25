import os
import glob
import chardet

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.utils.parsers.game_data.IKFSReader import IKFSReader


class KFSReader(IKFSReader):

	def __init__(self, config: Config = Provide[Container.config]):
		self._config = config

	def read_data_files(
		self,
		game_id: int,
		patterns: list[str],
		encoding: str | None = None
	) -> list[str]:
		"""
		Read data files from extracted data directory (searches recursively in all session subdirectories)

		Supports glob patterns for dynamic file discovery.

		:param game_id:
			Game ID (builds path as /tmp/game_<id>/data/**, searches recursively)
		:param patterns:
			List of filenames or glob patterns (e.g., ['items*.txt', 'spells.txt'])
		:param encoding:
			Text encoding (default: None for auto-detection)
		:return:
			List of file contents as strings from all matching files across all sessions
		:raises FileNotFoundError:
			If no files match pattern or directory not found
		"""
		data_dir = os.path.join(self._config.tmp_dir, f'game_{game_id}', 'data')
		return self._read_files_from_dir(data_dir, patterns, encoding)

	def read_loc_files(
		self,
		game_id: int,
		patterns: list[str],
		encoding: str = 'utf-16-le'
	) -> list[str]:
		"""
		Read localization files from extracted loc directory (searches recursively in all session subdirectories)

		Supports glob patterns for dynamic file discovery.

		:param game_id:
			Game ID (builds path as /tmp/game_<id>/loc/**, searches recursively)
		:param patterns:
			List of filenames or glob patterns (e.g., ['rus_*.lng', 'eng_items.lng'])
		:param encoding:
			Text encoding (default: utf-16-le)
		:return:
			List of file contents as strings from all matching files across all sessions
		:raises FileNotFoundError:
			If no files match pattern or directory not found
		"""
		loc_dir = os.path.join(self._config.tmp_dir, f'game_{game_id}', 'loc')
		print(f"Loc dir: {loc_dir}, patterns: {patterns}")
		return self._read_files_from_dir(loc_dir, patterns, encoding)

	def _read_files_from_dir(
		self,
		directory: str,
		patterns: list[str],
		encoding: str | None
	) -> list[str]:
		"""
		Read files from specified directory

		Supports glob patterns for dynamic file discovery.

		:param directory:
			Directory path
		:param patterns:
			List of filenames or glob patterns
		:param encoding:
			Text encoding (None for auto-detection)
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
		paths = self._expand_patterns(directory, patterns)

		if not paths:
			raise FileNotFoundError(
				f"No files found matching patterns {patterns} in directory '{directory}'"
			)

		results = []
		for path in paths:
			content = self._read_file(path, encoding)
			results.append(content)

		return results

	@staticmethod
	def _expand_patterns(directory: str, patterns: list[str]) -> list[str]:
		"""
		Expand glob patterns to actual filenames (searches recursively in all subdirectories)

		:param directory:
			Directory path
		:param patterns:
			List of filenames or glob patterns
		:return:
			Sorted list of unique filenames (basenames only)
		"""
		all_files = []

		for pattern in patterns:
			# Build recursive pattern to search all subdirectories
			full_pattern = os.path.join(directory, '**', pattern)

			# Expand glob pattern recursively
			matched_paths = glob.glob(full_pattern, recursive=True)
			print(f"Matched paths: {matched_paths}")
			all_files += matched_paths

		print(f"All files: {all_files}")
		# Return sorted list
		return sorted(set(all_files))

	def _read_file(
		self,
		path: str,
		encoding: str | None
	) -> str:
		"""
		Read single file from directory (searches recursively if not found at root)

		:param encoding:
			Text encoding (None for auto-detection)
		:return:
			File content as string
		:raises FileNotFoundError:
			If file not found
		"""
		# Try direct path first

		with open(path, 'rb') as file:
			content_bytes = file.read()

		try:
			return self._decode_content(content_bytes, encoding)
		except UnicodeDecodeError as e:
			raise UnicodeDecodeError(
				e.encoding,
				e.object,
				e.start,
				e.end,
				f"Failed to decode file '{path}': {e.reason}"
			) from e

	@staticmethod
	def _decode_content(content: bytes, encoding: str | None) -> str:
		"""
		Decode file content with automatic encoding detection

		Uses chardet to detect encoding when encoding is None, otherwise tries specified encoding first

		:param content:
			Raw file content as bytes
		:param encoding:
			Primary encoding to try (None for auto-detection using chardet)
		:return:
			Decoded string
		:raises UnicodeDecodeError:
			If content cannot be decoded
		"""
		encodings_to_try = []

		if encoding is None:
			encodings_to_try.extend(['utf-16-le', 'utf-8'])

			detected = chardet.detect(content)
			detected_encoding = detected.get('encoding')
			confidence = detected.get('confidence', 0)

			if detected_encoding and confidence > 0.7:
				detected_lower = detected_encoding.lower()
				if detected_lower not in encodings_to_try:
					encodings_to_try.append(detected_lower)

			encodings_to_try.append('iso-8859-1')
		else:
			encodings_to_try.append(encoding)
			if 'utf-16-le' not in encodings_to_try:
				encodings_to_try.append('utf-16-le')
			if 'utf-8' not in encodings_to_try:
				encodings_to_try.append('utf-8')
			if 'iso-8859-1' not in encodings_to_try:
				encodings_to_try.append('iso-8859-1')

		last_error = None
		for enc in encodings_to_try:
			try:
				decoded = content.decode(enc)
				if decoded.startswith('\ufeff'):
					decoded = decoded[1:]

				if encoding is None and not KFSReader._is_valid_decoded_content(decoded):
					continue

				return decoded
			except (UnicodeDecodeError, LookupError) as e:
				last_error = e
				continue

		raise UnicodeDecodeError(
			last_error.encoding if isinstance(last_error, UnicodeDecodeError) else 'unknown',
			content,
			0,
			len(content),
			f"Failed to decode content with any of: {', '.join(encodings_to_try)}"
		) from last_error

	@staticmethod
	def _is_valid_decoded_content(decoded: str) -> bool:
		"""
		Check if decoded content looks valid (not garbage from wrong encoding)

		:param decoded:
			Decoded string
		:return:
			True if content looks valid, False if looks like encoding error
		"""
		if not decoded:
			return True

		sample = decoded[:500]
		ascii_printable = sum(1 for c in sample if 32 <= ord(c) <= 126 or c in '\n\r\t')
		ascii_ratio = ascii_printable / len(sample)

		return ascii_ratio > 0.5
