import os
import glob
import shutil
import zipfile
from collections import defaultdict

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.utils.parsers.game_data.IKFSExtractor import IKFSExtractor


class KFSExtractor(IKFSExtractor):

	def __init__(self, config: Config = Provide[Container.config]):
		self._game_data_path = config.game_data_path
		self._archive_patterns = config.archive_patterns

	def extract_archives(self, game_name: str) -> str:
		"""
		Extract all game archives to /tmp/<game_name>/

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:return:
			Path to extraction root (/tmp/<game_name>/)
		"""
		extraction_root = f'/tmp/{game_name}'

		self._cleanup_previous_extraction(game_name)

		game_path = os.path.join(self._game_data_path, game_name)
		archive_patterns = self._build_archive_patterns(game_path)

		archive_paths = self._resolve_archive_patterns(archive_patterns)

		archive_groups = self._group_archives_by_basename(archive_paths)

		for basename, paths in archive_groups.items():
			self._extract_archive_group(
				archive_paths=paths,
				extraction_root=extraction_root,
				basename=basename
			)

		return extraction_root

	def _cleanup_previous_extraction(self, game_name: str) -> None:
		"""
		Delete /tmp/<game_name>/ directory if exists

		:param game_name:
			Game name
		"""
		extraction_root = f'/tmp/{game_name}'
		if os.path.exists(extraction_root):
			shutil.rmtree(extraction_root)

	def _build_archive_patterns(self, game_path: str) -> list[str]:
		"""
		Build archive patterns for extraction

		:param game_path:
			Absolute path to game directory
		:return:
			List of glob patterns
		"""
		return [
			pattern.format(game_path=game_path)
			for pattern in self._archive_patterns
		]

	def _resolve_archive_patterns(self, patterns: list[str]) -> list[str]:
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

	def _get_archive_basename(self, archive_path: str) -> str:
		"""
		Extract archive basename without .kfs extension

		:param archive_path:
			Full path to archive
		:return:
			Archive basename (e.g., 'ses', 'loc_ses_eng')
		"""
		filename = os.path.basename(archive_path)
		return filename[:-4] if filename.endswith('.kfs') else filename

	def _group_archives_by_basename(
		self,
		archive_paths: list[str]
	) -> dict[str, list[str]]:
		"""
		Group archives by basename for merging

		:param archive_paths:
			List of archive paths
		:return:
			Dictionary mapping basename to list of archive paths
		"""
		groups: dict[str, list[str]] = defaultdict(list)

		for path in archive_paths:
			basename = self._get_archive_basename(path)
			groups[basename].append(path)

		for basename in groups:
			groups[basename] = sorted(groups[basename])

		return dict(groups)

	def _extract_archive_group(
		self,
		archive_paths: list[str],
		extraction_root: str,
		basename: str
	) -> None:
		"""
		Extract archives with same basename to single directory

		:param archive_paths:
			List of archive paths with same basename
		:param extraction_root:
			Root extraction directory
		:param basename:
			Archive basename
		"""
		target_dir = os.path.join(extraction_root, basename)
		os.makedirs(target_dir, exist_ok=True)

		for archive_path in archive_paths:
			self._extract_archive_to_dir(archive_path, target_dir)

	def _extract_archive_to_dir(
		self,
		archive_path: str,
		target_dir: str
	) -> None:
		"""
		Extract archive contents to target directory

		:param archive_path:
			Path to archive file
		:param target_dir:
			Directory to extract files into
		"""
		try:
			with zipfile.ZipFile(archive_path, 'r') as archive:
				for file_info in archive.filelist:
					file_path = file_info.filename
					target_path = os.path.join(target_dir, file_path)

					if os.path.exists(target_path):
						print(
							f"Warning: File '{file_path}' from '{archive_path}' "
							f"overwrites existing file"
						)

					archive.extract(file_info, target_dir)

		except zipfile.BadZipFile as e:
			raise zipfile.BadZipFile(
				f"Invalid ZIP archive: {archive_path}"
			) from e
