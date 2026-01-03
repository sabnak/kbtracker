from pathlib import Path
from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.core.Config import Config
from src.domain.game.ISaveFileService import ISaveFileService
from src.utils.parsers.save_data.IHeroSaveParser import IHeroSaveParser


class SaveFileService(ISaveFileService):

	@inject
	def __init__(
		self,
		config: Config = Provide[Container.config],
		hero_parser: IHeroSaveParser = Provide[Container.hero_save_parser]
	):
		self._config = config
		self._hero_parser = hero_parser

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
			if save_dir.is_dir() and save_dir.name.isdigit():
				saves.append({
					'name': save_dir.name,
					'path': str(save_dir),
					'timestamp': int(save_dir.name)
				})

		saves.sort(key=lambda x: x['timestamp'], reverse=True)

		return {
			game_path: saves[:limit]
		}

	def scan_save_file(
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
