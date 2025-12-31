import os
import zipfile

from src.domain.game.utils.IKFSExtractor import IKFSExtractor


class KFSExtractor(IKFSExtractor):

	def extract(self, sessions_path: str, tables: list[str]) -> list[str]:
		"""
		Extract specified files from KFS archives

		Scans sessions directory subdirectories for requested .kfs archives,
		extracts specified files, and returns their contents as strings.

		:return:
			List of file contents as UTF-16 LE decoded strings,
			in the same order as tables parameter
		:raises FileNotFoundError:
			If any requested archive not found in sessions directory
		:raises KeyError:
			If requested file not found in archive
		:raises UnicodeDecodeError:
			If file content cannot be decoded
		"""
		archive_files_map = self._parse_tables(tables)
		archive_names = list(archive_files_map.keys())
		archive_paths = self._find_archives(sessions_path, archive_names)

		results = []
		for table in tables:
			archive_name, file_path = table.split('/', 1)
			archive_path = archive_paths[archive_name]
			content = self._extract_from_archive(archive_path, file_path)
			results.append(content)

		return results

	def _parse_tables(self, tables: list[str]) -> dict[str, list[str]]:
		"""
		Parse tables parameter into archive to files mapping

		:return:
			Dictionary mapping archive names to lists of files to extract
		"""
		archive_files_map: dict[str, list[str]] = {}
		for table in tables:
			archive_name, file_path = table.split('/', 1)
			if archive_name not in archive_files_map:
				archive_files_map[archive_name] = []
			archive_files_map[archive_name].append(file_path)
		return archive_files_map

	def _find_archives(self, sessions_path: str, archive_names: list[str]) -> dict[str, str]:
		"""
		Scan sessions directory subdirectories for .kfs archives

		:param archive_names:
			List of archive names to find
		:return:
			Dictionary mapping archive names to their full paths
		:raises FileNotFoundError:
			If any requested archive not found
		"""
		found_archives: dict[str, str] = {}

		if not os.path.exists(sessions_path):
			raise FileNotFoundError(
				f"Sessions directory not found: {sessions_path}"
			)

		for entry in os.listdir(sessions_path):
			entry_path = os.path.join(sessions_path, entry)
			if os.path.isdir(entry_path):
				for archive_name in archive_names:
					archive_path = os.path.join(entry_path, archive_name)
					if os.path.exists(archive_path) and archive_name not in found_archives:
						found_archives[archive_name] = archive_path

		for archive_name in archive_names:
			if archive_name not in found_archives:
				raise FileNotFoundError(
					f"Archive '{archive_name}' not found in {sessions_path}"
				)

		return found_archives

	def _extract_from_archive(self, archive_path: str, file_path: str) -> str:
		"""
		Extract file from ZIP archive and decode content

		:param archive_path:
			Full path to .kfs (ZIP) archive
		:param file_path:
			Path to file within archive
		:return:
			Decoded file content as string
		:raises zipfile.BadZipFile:
			If archive is not a valid ZIP file
		:raises KeyError:
			If file not found in archive
		"""
		try:
			with zipfile.ZipFile(archive_path, 'r') as archive:
				if file_path not in archive.namelist():
					raise KeyError(
						f"File '{file_path}' not found in archive '{archive_path}'"
					)
				content_bytes = archive.read(file_path)
				return self._decode_content(content_bytes)
		except zipfile.BadZipFile as e:
			raise zipfile.BadZipFile(
				f"Invalid ZIP archive: {archive_path}"
			) from e

	def _decode_content(self, content: bytes) -> str:
		"""
		Decode file content with proper encoding

		Tries UTF-16 LE first (primary encoding for KFS files),
		then falls back to UTF-8 if that fails.

		:param content:
			Raw file content as bytes
		:return:
			Decoded string
		:raises UnicodeDecodeError:
			If content cannot be decoded with either encoding
		"""
		try:
			return content.decode('utf-16-le')
		except UnicodeDecodeError:
			try:
				return content.decode('utf-8')
			except UnicodeDecodeError as e:
				raise UnicodeDecodeError(
					e.encoding,
					e.object,
					e.start,
					e.end,
					f"Failed to decode content with UTF-16 LE or UTF-8"
				) from e
