from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.utils.parsers import atom
from src.utils.parsers.game_data.IKFSReader import IKFSReader
from src.utils.parsers.game_data.IKFSUnitParser import IKFSUnitParser


class KFSUnitParser(IKFSUnitParser):

	@inject
	def __init__(
		self,
		reader: IKFSReader = Provide[Container.kfs_reader],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		"""
		Initialize KFS unit parser

		:param reader:
			KFS file reader
		:param localization_repository:
			Localization repository
		"""
		self._reader = reader
		self._localization_repository = localization_repository

	def parse(
		self,
		game_name: str,
		allowed_kb_ids: list[str] | None = None
	) -> list[Unit]:
		"""
		Extract and parse unit data from game files

		Skips units with class='spirit'. Raises exception for invalid atom files.

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:param allowed_kb_ids:
			Optional list of unit kb_ids to parse (for testing)
		:return:
			List of Unit entities with id=0 (spirits are skipped)
		:raises FileNotFoundError:
			When unit atom file not found
		:raises ValueError:
			When atom file has invalid structure
		"""
		unit_kb_ids = self._get_unit_kb_ids()

		if allowed_kb_ids:
			unit_kb_ids = [kb_id for kb_id in unit_kb_ids if kb_id in allowed_kb_ids]

		units = []
		for kb_id in unit_kb_ids:
			unit = self._parse_unit_file(game_name, kb_id)
			if unit is not None:
				units.append(unit)

		return units

	def _get_unit_kb_ids(self) -> list[str]:
		"""
		Get unit kb_ids from localization table

		Queries localization table for entries with tag='units'
		and kb_id starting with 'cpn_', excludes:
		- hints (cpn_hint_*)
		- names (*_name)
		- spawners (*_spawner)

		:return:
			List of unit kb_ids
		"""
		all_localizations = self._localization_repository.list_all(tag='units')

		unit_kb_ids = []
		for loc in all_localizations:
			if not loc.kb_id.startswith('cpn_'):
				continue
			unit_kb_id = loc.kb_id[4:]
			if not self._is_kb_id_valid(unit_kb_id):
				continue
			unit_kb_ids.append(unit_kb_id)

		return unit_kb_ids

	@staticmethod
	def _is_kb_id_valid(kb_id: str) -> bool:
		if kb_id.startswith('hint_'):
			return False
		if kb_id.endswith('_name') or kb_id.endswith('_spawner'):
			return False
		return True

	def _parse_unit_file(self, game_name: str, kb_id: str) -> Unit | None:
		"""
		Parse single unit atom file

		:param game_name:
			Game name
		:param kb_id:
			Unit kb_id (e.g., 'bowman')
		:return:
			Unit entity or None if unit class is 'spirit'
		:raises FileNotFoundError:
			When atom file not found
		:raises ValueError:
			When atom file has invalid structure (missing sections, wrong types, etc.)
		"""
		atom_filename = f"{kb_id}.atom"

		try:
			contents = self._reader.read_data_files(game_name, [atom_filename])
		except FileNotFoundError as e:
			raise FileNotFoundError(
				f"Unit atom file not found: {atom_filename} for unit {kb_id}"
			) from e

		if not contents:
			raise ValueError(f"Unit atom file '{atom_filename}' returned empty content")

		content = contents[0]
		parsed = atom.loads(content)

		if 'main' not in parsed:
			raise ValueError(f"Unit '{kb_id}': atom file missing 'main' section")

		main_section = parsed['main']
		if not isinstance(main_section, dict):
			raise ValueError(f"Unit '{kb_id}': 'main' section is not a dict")

		unit_class_str = main_section.get('class', 'chesspiece')

		if unit_class_str == 'spirit':
			return None

		if 'arena_params' not in parsed:
			raise ValueError(f"Unit '{kb_id}': atom file missing 'arena_params' section")

		arena_params = parsed['arena_params']
		if not isinstance(arena_params, dict):
			raise ValueError(f"Unit '{kb_id}': 'arena_params' section is not a dict")

		try:
			unit_class = UnitClass(unit_class_str)
		except ValueError:
			unit_class = UnitClass.CHESSPIECE

		processed_params = self._process_arena_params(arena_params)

		return Unit(
			id=0,
			kb_id=kb_id,
			name='',
			unit_class=unit_class,
			params=processed_params
		)

	def _process_arena_params(self, arena_params: dict) -> dict:
		"""
		Process arena_params dictionary

		Splits features_hints and attacks into lists

		:param arena_params:
			Raw arena_params from atom file
		:return:
			Processed params with lists for specific fields
		"""
		processed = dict(arena_params)

		if 'features_hints' in processed and isinstance(processed['features_hints'], str):
			processed['features_hints'] = self._split_comma_separated(
				processed['features_hints']
			)

		if 'attacks' in processed and isinstance(processed['attacks'], str):
			processed['attacks'] = self._split_comma_separated(
				processed['attacks']
			)

		return processed

	@staticmethod
	def _split_comma_separated(value: str) -> list[str]:
		"""
		Split comma-separated string into list

		:param value:
			Comma-separated string
		:return:
			List of trimmed strings
		"""
		if not value:
			return []
		return [item.strip() for item in value.split(',')]
