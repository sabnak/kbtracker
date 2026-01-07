import hashlib
from pathlib import Path
from typing import Any

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.core.Config import Config
from src.domain import ProfileEntity
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.utils.parsers.save_data.IHeroSaveParser import IHeroSaveParser
from src.utils.parsers.save_data.IShopInventoryParser import IShopInventoryParser


class SaveFileService(ISaveFileService):

	def __init__(
		self,
		config: Config = Provide[Container.config],
		shop_parser: IShopInventoryParser = Provide[Container.shop_inventory_parser],
		hero_parser: IHeroSaveParser = Provide[Container.hero_save_parser]
	):
		self._config = config
		self._hero_parser = hero_parser
		self._shop_parser = shop_parser

	def list_save_directories(
		self,
		game_path: str,
		limit: int = 100
	) -> dict[str, list[dict]]:
		"""
		List save directories grouped by game name

		:param game_path:
			Game path (e.g., "Darkside")
		:param limit:
			Maximum number of saves to return per game
		:return:
			Dictionary with game names as keys and list of save info dicts
		"""
		save_base = Path(self._config.game_save_path)
		game_save_dir = save_base / game_path

		if not game_save_dir.exists():
			return {}

		saves = []
		for save_dir in game_save_dir.iterdir():
			if save_dir.is_dir():
				timestamp = int(save_dir.stat().st_mtime)
				saves.append({
					'name': save_dir.name,
					'path': str(save_dir),
					'timestamp': timestamp
				})

		saves.sort(key=lambda x: x['timestamp'], reverse=True)

		return {
			game_path: saves[:limit]
		}

	def scan_hero_data(
		self,
		game_path: str,
		save_dir_name: str
	) -> dict[str, str]:
		"""
		Scan save file and extract hero data

		:param game_path:
			Game path (e.g., "Darkside")
		:param save_dir_name:
			Save directory name (timestamp like "1707047253")
		:return:
			Hero data dictionary with first_name, second_name, and full_name
		"""
		save_base = Path(self._config.game_save_path)
		data_file = save_base / game_path / save_dir_name / "data"

		if not data_file.exists():
			raise FileNotFoundError(f"Save data file not found: {data_file}")

		hero_data = self._hero_parser.parse(data_file)

		# Compute full name from first and second names
		first_name = hero_data.get('first_name', '')
		second_name = hero_data.get('second_name', '')
		hero_data['full_name'] = f"{first_name} {second_name}".strip()

		return hero_data

	def scan_shop_inventory(self, save_path: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
		return self._shop_parser.parse(save_path)

	def find_profile_most_recent_save(self, profile: ProfileEntity) -> Path:
		game_dir = profile.save_dir.split('/')[0]
		save_path = Path(self._config.game_save_path) / game_dir

		lif_files = list(save_path.glob("*/data"))
		lif_files = sorted(lif_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]

		for lif_file in lif_files:
			try:
				hero_data = self._hero_parser.parse(lif_file)
				full_name = f"{hero_data['first_name']} {hero_data['second_name']}"
				computed_hash = self.compute_hash(full_name)

				if computed_hash == profile.hash:
					return lif_file
			except Exception:
				continue

		raise FileNotFoundError(f"No matching save found for profile {profile.id}")

	def compute_hash(self, full_name: str) -> str:
		"""
		Compute hash from hero full name

		:param full_name:
			Hero's full name
		:return:
			Hash as MD5 hex string
		"""
		return hashlib.md5(full_name.encode('utf-8')).hexdigest()
