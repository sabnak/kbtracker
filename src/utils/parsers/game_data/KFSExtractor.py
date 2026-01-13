import glob
import os
import shutil
import zipfile

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.app.entities.Game import Game
from src.utils.parsers.game_data.IKFSExtractor import IKFSExtractor


class KFSExtractor(IKFSExtractor):

	def __init__(self, config: Config = Provide[Container.config]):
		self._config = config

	def extract_archives(self, game: Game) -> str:
		"""
		Extract all game archives to /tmp/<game.path>/ with session-specific subdirectories

		Data archives go to /tmp/<game.path>/data/<session>/
		Localization archives go to /tmp/<game.path>/loc/<session>/
		Main data archive goes to /tmp/<game.path>/data/data/ and /tmp/<game.path>/loc/data/

		:param game:
			Game entity with path and sessions list
		:return:
			Path to extraction root (/tmp/<game.path>/)
		"""
		extraction_root = os.path.join(self._config.tmp_dir, game.path)

		self._cleanup_previous_extraction(game.path)

		game_path = os.path.join(self._config.game_data_path, game.path)

		# Extract main data archive to data/ subdirectory
		data_archive_paths = self._get_data_archive_paths(game_path)
		if data_archive_paths:
			self._extract_to_session(data_archive_paths, extraction_root, "data", "1")

		# Extract session-specific archives
		for i, session in enumerate(game.sessions):
			session_archive_paths = self._get_session_archive_paths(game_path, session)
			if session_archive_paths:
				self._extract_to_session(session_archive_paths, extraction_root, session, str(i + 2))

		return extraction_root

	def _cleanup_previous_extraction(self, game_path: str) -> None:
		"""
		Delete /tmp/<game_path>/ directory if exists

		:param game_path:
			Game path
		"""
		extraction_root = os.path.join(self._config.tmp_dir, game_path)
		if os.path.exists(extraction_root):
			shutil.rmtree(extraction_root)

	def _get_data_archive_paths(self, game_path: str) -> list[str]:
		"""
		Get paths to main data archive

		:param game_path:
			Absolute path to game directory
		:return:
			List of matched data archive paths (may be empty)
		"""
		data_path = self._config.data_archive_path.format(game_path=game_path)
		return glob.glob(data_path)

	def _get_session_archive_paths(
		self,
		game_path: str,
		session: str
	) -> list[str]:
		"""
		Get paths to session-specific archives

		:param game_path:
			Absolute path to game directory
		:param session:
			Session name
		:return:
			List of matched session archive paths (may be empty)
		"""
		pattern = self._config.session_archives_pattern.format(
			game_path=game_path,
			session=session
		)
		return glob.glob(pattern)

	def _extract_to_session(
		self,
		archive_paths: list[str],
		extraction_root: str,
		session_name: str,
		prefix: str
	) -> None:
		"""
		Extract archives to session-specific subdirectories

		:param archive_paths:
			List of archive paths to extract
		:param extraction_root:
			Root extraction directory (/tmp/<game.path>/)
		:param session_name:
			Session name (e.g., 'data', 'darkside', 'lightside')
		"""
		data_dir = os.path.join(extraction_root, 'data', f"{prefix}-{session_name}")
		loc_dir = os.path.join(extraction_root, 'loc', f"{prefix}-{session_name}")

		os.makedirs(data_dir, exist_ok=True)
		os.makedirs(loc_dir, exist_ok=True)

		for archive_path in sorted(archive_paths):
			self._extract_archive_flat(
				archive_path,
				extraction_root,
				data_dir,
				loc_dir,
				session_name
			)


	@staticmethod
	def _extract_archive_flat(
		archive_path: str,
		extraction_root: str,
		data_dir: str,
		loc_dir: str,
		session_name: str
	) -> None:
		"""
		Extract single archive with flat structure and extension filtering

		:param archive_path:
			Path to archive file
		:param extraction_root:
			Root extraction directory
		:param data_dir:
			Directory for data files (.atom, .txt)
		:param loc_dir:
			Directory for localization files (.lng)
		:param session_name:
			Session name for logging (e.g., 'data', 'darkside')
		"""
		try:
			with zipfile.ZipFile(archive_path, 'r') as archive:
				for file_info in archive.filelist:
					if file_info.is_dir():
						continue

					filename = os.path.basename(file_info.filename)
					ext = os.path.splitext(filename)[1].lower()

					if ext not in ['.atom', '.txt', '.lng']:
						continue

					target_subdir_name = 'loc' if ext == '.lng' else 'data'
					target_dir = loc_dir if ext == '.lng' else data_dir
					target_path = os.path.join(target_dir, filename)

					if os.path.exists(target_path):
						print(
							f"Info: File '{filename}' from archive "
							f"'{os.path.basename(archive_path)}' overwrites existing file "
							f"in '{target_subdir_name}/{session_name}/' directory. This is expected for modded games."
						)

					content = archive.read(file_info)
					with open(target_path, 'wb') as f:
						f.write(content)

		except zipfile.BadZipFile as e:
			raise zipfile.BadZipFile(
				f"Invalid ZIP archive: {archive_path}"
			) from e
