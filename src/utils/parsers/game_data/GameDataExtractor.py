import os
import shutil

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.app.entities.Game import Game
from src.utils.parsers.game_data.IGameDataExtractor import IGameDataExtractor
from src.utils.parsers.game_data.IKFSExtractor import IKFSExtractor


class GameDataExtractor(IGameDataExtractor):

	_DATA_EXTENSIONS: tuple[str, ...] = ('.atom', '.txt')
	_LOC_EXTENSION: str = '.lng'

	def __init__(
		self,
		kfs_extractor: IKFSExtractor = Provide[Container.kfs_extractor],
		config: Config = Provide[Container.config]
	):
		self._kfs_extractor = kfs_extractor
		self._config = config

	def extract(self, game: Game) -> str:
		"""
		Prepare a flat copy of all game data under /tmp/game_<game.id>/

		Archives are extracted first (this also resets the extraction root),
		then loose files from each session are copied on top so that both
		packed and unpacked sessions end up in the same flat structure.

		:param game:
			Game entity with path and sessions list
		:return:
			Path to extraction root (/tmp/game_<game.id>/)
		"""
		extraction_root = self._kfs_extractor.extract_archives(game)
		game_path = self._resolve_game_path(game.path)

		self._copy_loose_files(self._data_source(game_path), extraction_root, "data")
		for session in game.sessions:
			session_source = self._session_source(game_path, session)
			self._copy_loose_files(session_source, extraction_root, session)

		return extraction_root

	def cleanup(self, game: Game) -> None:
		"""
		Clean up temporary extracted files for the given game

		:param game:
			Game entity to clean up temporary files for
		"""
		self._kfs_extractor.cleanup_extraction(game)

	def _resolve_game_path(self, game_path: str) -> str:
		"""
		Resolve game path based on mode

		In localhost mode (game_data_path=:local), game_path is already absolute.
		In Docker mode, game_path is relative to game_data_path.

		:param game_path:
			Game path from database
		:return:
			Absolute path to game directory
		"""
		if self._config.game_data_path == ":local":
			return game_path
		return os.path.join(self._config.game_data_path, game_path)

	def _data_source(self, game_path: str) -> str:
		"""
		Resolve the loose main data directory for the game

		:param game_path:
			Absolute path to game directory
		:return:
			Absolute path to the main data directory
		"""
		return self._config.data_path.format(game_path=game_path)

	def _session_source(self, game_path: str, session: str) -> str:
		"""
		Resolve the loose data directory for a single session

		:param game_path:
			Absolute path to game directory
		:param session:
			Session name
		:return:
			Absolute path to the session directory
		"""
		return self._config.session_path.format(game_path=game_path, session=session)

	def _copy_loose_files(
		self,
		source_dir: str,
		extraction_root: str,
		session_name: str
	) -> None:
		"""
		Copy loose data/localization files from a source directory into the flat structure

		Walks the source recursively, keeping only relevant extensions and
		dropping any nested directory structure. Missing source directories
		(e.g. fully packed sessions) are silently skipped.

		:param source_dir:
			Directory holding unpacked game files
		:param extraction_root:
			Root extraction directory (/tmp/game_<game.id>/)
		:param session_name:
			Session name used to namespace the target subdirectory
		"""
		if not os.path.isdir(source_dir):
			return

		data_dir = os.path.join(extraction_root, 'data', f"loose-{session_name}")
		loc_dir = os.path.join(extraction_root, 'loc', f"loose-{session_name}")

		for root, _, files in os.walk(source_dir):
			for filename in files:
				self._copy_file_flat(os.path.join(root, filename), data_dir, loc_dir, session_name)

	def _copy_file_flat(
		self,
		source_path: str,
		data_dir: str,
		loc_dir: str,
		session_name: str
	) -> None:
		"""
		Copy a single loose file into the matching flat target directory

		:param source_path:
			Absolute path to the source file
		:param data_dir:
			Target directory for data files (.atom, .txt)
		:param loc_dir:
			Target directory for localization files (.lng)
		:param session_name:
			Session name for logging
		"""
		ext = os.path.splitext(source_path)[1].lower()
		target_dir = self._target_dir_for(ext, data_dir, loc_dir)
		if target_dir is None:
			return

		os.makedirs(target_dir, exist_ok=True)
		filename = os.path.basename(source_path)
		target_path = os.path.join(target_dir, filename)

		if os.path.exists(target_path):
			print(
				f"Info: Loose file '{filename}' from session '{session_name}' "
				f"overwrites existing file. This is expected for modded games."
			)

		shutil.copyfile(source_path, target_path)

	def _target_dir_for(
		self,
		ext: str,
		data_dir: str,
		loc_dir: str
	) -> str | None:
		"""
		Resolve the target directory for a file extension

		:param ext:
			Lowercased file extension including the leading dot
		:param data_dir:
			Target directory for data files (.atom, .txt)
		:param loc_dir:
			Target directory for localization files (.lng)
		:return:
			Target directory, or None if the extension is not relevant
		"""
		if ext == self._LOC_EXTENSION:
			return loc_dir
		if ext in self._DATA_EXTENSIONS:
			return data_dir
		return None
