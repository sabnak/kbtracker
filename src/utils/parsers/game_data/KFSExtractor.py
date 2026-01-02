import glob
import os
import shutil
import zipfile

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.utils.parsers.game_data.IKFSExtractor import IKFSExtractor


class KFSExtractor(IKFSExtractor):

	def __init__(self, config: Config = Provide[Container.config]):
		self._config = config

	def extract_archives(self, game_name: str) -> str:
		"""
		Extract all game archives to /tmp/<game_name>/

		Data archives go to /tmp/<game_name>/data/
		Localization archives go to /tmp/<game_name>/loc/

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:return:
			Path to extraction root (/tmp/<game_name>/)
		"""
		extraction_root = os.path.join(self._config.tmp_dir, game_name)

		self._cleanup_previous_extraction(game_name)

		game_path = os.path.join(self._config.game_data_path, game_name)

		# Extract data archives
		data_patterns = self._build_archive_patterns(game_path, self._config.data_archive_patterns)
		data_paths = self._resolve_archive_patterns(data_patterns)
		self._extract_archives_to_subdir(data_paths, extraction_root, 'data')

		# Extract localization archives
		loc_patterns = self._build_archive_patterns(game_path, self._config.loc_archive_patterns)
		loc_paths = self._resolve_archive_patterns(loc_patterns)
		self._extract_archives_to_subdir(loc_paths, extraction_root, 'loc')

		return extraction_root

	@staticmethod
	def _cleanup_previous_extraction(game_name: str) -> None:
		"""
		Delete /tmp/<game_name>/ directory if exists

		:param game_name:
			Game name
		"""
		extraction_root = f'/tmp/{game_name}'
		if os.path.exists(extraction_root):
			shutil.rmtree(extraction_root)

	@staticmethod
	def _build_archive_patterns(game_path: str, patterns: list[str]) -> list[str]:
		"""
		Build archive patterns for extraction

		:param game_path:
			Absolute path to game directory
		:param patterns:
			List of pattern templates
		:return:
			List of glob patterns
		"""
		return [
			pattern.format(game_path=game_path)
			for pattern in patterns
		]

	@staticmethod
	def _resolve_archive_patterns(patterns: list[str]) -> list[str]:
		"""
		Convert glob patterns to actual archive paths

		:param patterns:
			List of glob patterns
		:return:
			List of resolved archive paths
		:raises FileNotFoundError:
			If no archives found for any pattern
		"""
		all_paths = []

		for pattern in patterns:
			matched_paths = glob.glob(pattern)

			if not matched_paths:
				raise FileNotFoundError(
					f"No archives found matching pattern: {pattern}"
				)

			all_paths.extend(matched_paths)

		return all_paths

	def _extract_archives_to_subdir(
		self,
		archive_paths: list[str],
		extraction_root: str,
		target_subdir: str
	) -> None:
		"""
		Extract archives to target subdirectory (data/ or loc/)

		:param archive_paths:
			List of archive paths to extract
		:param extraction_root:
			Root extraction directory (/tmp/<game_name>/)
		:param target_subdir:
			Target subdirectory name ('data' or 'loc')
		"""
		if not archive_paths:
			return

		target_dir = os.path.join(extraction_root, target_subdir)
		os.makedirs(target_dir, exist_ok=True)

		for archive_path in sorted(archive_paths):
			self._extract_archive_to_dir(archive_path, target_dir, target_subdir)

	@staticmethod
	def _extract_archive_to_dir(
		archive_path: str,
		target_dir: str,
		target_subdir: str = ''
	) -> None:
		"""
		Extract archive contents to target directory

		:param archive_path:
			Path to archive file
		:param target_dir:
			Directory to extract files into
		:param target_subdir:
			Optional subdirectory name for logging context
		"""
		try:
			with zipfile.ZipFile(archive_path, 'r') as archive:
				for file_info in archive.filelist:
					file_path = file_info.filename
					target_path = os.path.join(target_dir, file_path)

					if os.path.exists(target_path):
						subdir_msg = f" in '{target_subdir}/' directory" if target_subdir else ""
						print(
							f"Info: File '{file_path}' from archive "
							f"'{os.path.basename(archive_path)}' overwrites existing file"
							f"{subdir_msg}. This is expected for modded games."
						)

					archive.extract(file_info, target_dir)

		except zipfile.BadZipFile as e:
			raise zipfile.BadZipFile(
				f"Invalid ZIP archive: {archive_path}"
			) from e
