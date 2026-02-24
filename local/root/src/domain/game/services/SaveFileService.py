import hashlib
import re
from glob import glob
from logging import Logger
from pathlib import Path
from typing import Any

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain import ProfileEntity
from src.domain.app.entities.Game import Game
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.utils.parsers.save_data.IHeroSaveParser import IHeroSaveParser
from src.utils.parsers.save_data.ISaveDataParser import ISaveDataParser
from src.utils.parsers.save_data.SaveFileData import SaveFileData


class SaveFileService(ISaveFileService):

	def __init__(
		self,
		config: Config = Provide[Container.config],
		save_data_parser: ISaveDataParser = Provide[Container.save_data_parser],
		hero_data_parser: IHeroSaveParser = Provide[Container.hero_save_parser],
		logger: Logger = Provide[Container.logger]
	):
		self._config = config
		self._hero_parser = hero_data_parser
		self._shop_parser = save_data_parser
		self._logger = logger

	def list_save_directories(
		self,
		game: Game,
		limit: int = 100
	) -> dict[str, list[dict]]:
		"""
		List save directories grouped by game name

		:param game:
			Game entity containing saves_pattern
		:param limit:
			Maximum number of saves to return per game
		:return:
			Dictionary with game names as keys and list of save info dicts
		"""
		save_base = Path(self._config.game_save_path)
		pattern_path = save_base / game.saves_pattern
		pattern_str = str(pattern_path)

		matching_paths = glob(pattern_str)

		saves = []
		for path_str in matching_paths:
			save_path = Path(path_str)
			timestamp = int(save_path.stat().st_mtime)

			save_name = save_path.name
			if save_path.suffix == '.sav':
				save_name = save_path.stem

			saves.append({
				'name': save_name,
				'path': str(save_path),
				'timestamp': timestamp
			})

		saves.sort(key=lambda x: x['timestamp'], reverse=True)

		return {
			game.path: saves[:limit]
		}

	def scan_hero_data(
		self,
		game: Game,
		save_path: str
	) -> dict[str, str]:
		"""
		Scan save file and extract hero data

		:param game:
			Game entity containing saves_pattern
		:param save_path:
			Absolute save path
		:return:
			Hero data dictionary with first_name, second_name, and full_name
		"""
		save_path = Path(save_path)

		if not save_path.exists():
			raise FileNotFoundError(f"Save not found: {save_path}")

		hero_data = self._hero_parser.parse(save_path)

		first_name = hero_data.get('first_name', '')
		second_name = hero_data.get('second_name', '')
		hero_data['full_name'] = f"{first_name} {second_name}".strip()

		return hero_data

	def scan_save_data(self, save_path: Path) -> SaveFileData:
		return self._shop_parser.parse(save_path)

	def find_profile_most_recent_save(self, profile: ProfileEntity) -> Path:
		"""
		Find most recent save file matching profile hash

		:param profile:
			Profile entity
		:return:
			Path to matching save file
		:raises FileNotFoundError:
			If no matching save found
		"""
		if not profile.game:
			raise FileNotFoundError(f"Profile {profile.id} has no associated game")

		save_base = Path(self._config.game_save_path)
		pattern_path = save_base / profile.game.saves_pattern
		pattern_str = str(pattern_path)

		matching_paths = glob(pattern_str)
		matching_paths = sorted(matching_paths, key=lambda p: Path(p).stat().st_mtime, reverse=True)[:5]

		self._logger.debug(f"Scanning saves by pattern: {pattern_str}. Matching paths: {matching_paths}")

		for save_path_str in matching_paths:
			save_path = Path(save_path_str)
			self._logger.debug(f"Scanning save: {save_path}")
			hero_data = self._hero_parser.parse(save_path)
			full_name = f"{hero_data['first_name']} {hero_data['second_name']}"
			computed_hash = self.compute_hash(full_name)
			self._logger.debug(f"Hero data: {hero_data}. Hash: {computed_hash}")

			if computed_hash == profile.hash:
				return save_path

		raise FileNotFoundError(f"No matching save found for profile {profile.id}. Pattern: {pattern_str}")

	def compute_hash(self, full_name: str) -> str:
		"""
		Compute hash from hero full name

		:param full_name:
			Hero's full name
		:return:
			Hash as MD5 hex string
		"""
		cleared_name = re.sub(r"\s+", "", full_name)
		return hashlib.md5(cleared_name.encode('utf-8')).hexdigest()
