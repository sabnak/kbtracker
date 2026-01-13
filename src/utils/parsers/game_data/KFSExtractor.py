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
		Extract all game archives to /tmp/<game.path>/

		Data archives go to /tmp/<game.path>/data/
		Localization archives go to /tmp/<game.path>/loc/

		:param game:
			Game entity with path and sessions list
		:return:
			Path to extraction root (/tmp/<game.path>/)
		"""
		extraction_root = os.path.join(self._config.tmp_dir, game.path)

		self._cleanup_previous_extraction(game.path)

		game_path = os.path.join(self._config.game_data_path, game.path)

		archive_paths = self._build_archive_paths_from_game(game, game_path)

		self._extract_archives_flat(archive_paths, extraction_root)

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

	def _build_archive_paths_from_game(
		self,
		game: Game,
		game_path: str
	) -> list[str]:
		"""
		Build list of archive paths from Game.sessions

		:param game:
			Game entity with sessions list
		:param game_path:
			Absolute path to game directory
		:return:
			List of resolved archive paths
		:raises FileNotFoundError:
			If no archives found
		"""
		paths = []

		data_path = self._config.data_archive_path.format(game_path=game_path)
		matched_data = glob.glob(data_path)
		paths.extend(matched_data)

		for session in game.sessions:
			pattern = self._config.session_archives_pattern.format(
				game_path=game_path,
				session=session
			)
			matched_session = glob.glob(pattern)
			paths.extend(matched_session)

		if not paths:
			raise FileNotFoundError(
				f"No archives found for game {game.path}"
			)

		return paths

	def _extract_archives_flat(
		self,
		archive_paths: list[str],
		extraction_root: str
	) -> None:
		"""
		Extract archives with flat structure and extension filtering

		Only files with extensions .atom, .txt, .lng are extracted.
		Files are extracted flat (no subdirectories).
		.lng files go to loc/, .atom and .txt go to data/

		:param archive_paths:
			List of archive paths to extract
		:param extraction_root:
			Root extraction directory (/tmp/<game.path>/)
		"""
		data_dir = os.path.join(extraction_root, 'data')
		loc_dir = os.path.join(extraction_root, 'loc')

		os.makedirs(data_dir, exist_ok=True)
		os.makedirs(loc_dir, exist_ok=True)

		for archive_path in sorted(archive_paths):
			self._extract_archive_flat(
				archive_path,
				extraction_root,
				data_dir,
				loc_dir
			)

	@staticmethod
	def _extract_archive_flat(
		archive_path: str,
		extraction_root: str,
		data_dir: str,
		loc_dir: str
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
							f"in '{target_subdir_name}/' directory. This is expected for modded games."
						)

					content = archive.read(file_info)
					with open(target_path, 'wb') as f:
						f.write(content)

		except zipfile.BadZipFile as e:
			raise zipfile.BadZipFile(
				f"Invalid ZIP archive: {archive_path}"
			) from e
