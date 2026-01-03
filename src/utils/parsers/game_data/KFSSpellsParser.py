from typing import Any

from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.utils.parsers import atom
from src.utils.parsers.game_data.IKFSReader import IKFSReader
from src.utils.parsers.game_data.IKFSSpellsParser import IKFSSpellsParser


class KFSSpellsParser(IKFSSpellsParser):

	@inject
	def __init__(
		self,
		reader: IKFSReader = Provide[Container.kfs_reader],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		"""
		Initialize KFS spell parser

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
	) -> dict[str, dict[str, Any]]:
		"""
		Extract and parse spell data from spells*.txt files

		Returns dictionary: {kb_id: {kb_id, profit, price, school,
		                     mana_cost, crystal_cost, data}}

		Battle spells (school 1-4):
		- Have 'levels' block with mana/crystal costs
		- mana_cost and crystal_cost are lists [mana1, mana2, mana3]

		Wandering spells (school 5):
		- Have 'action' field instead of 'levels'
		- mana_cost and crystal_cost are None

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:param allowed_kb_ids:
			Optional list of spell kb_ids to parse (for testing)
		:return:
			Dictionary mapping kb_id to raw spell data
		:raises FileNotFoundError:
			When spell file not found
		:raises ValueError:
			When spell file has invalid structure
		"""
		spell_kb_ids = self._get_spell_kb_ids()

		if allowed_kb_ids:
			spell_kb_ids = [kb_id for kb_id in spell_kb_ids if kb_id in allowed_kb_ids]

		spell_files = self._reader.read_data_files(game_name, ['spells*.txt'])

		if not spell_files:
			raise FileNotFoundError(f"Spell data files not found for game: {game_name}")

		result = {}
		for file_content in spell_files:
			parsed_spells = atom.loads(file_content)
			for spell_id, spell_data in parsed_spells.items():
				if spell_id.startswith('spell_'):
					kb_id = spell_id[6:]
					if kb_id in spell_kb_ids:
						processed = self._process_spell_data(kb_id, spell_data)
						if processed:
							result[kb_id] = processed

		return result

	def _get_spell_kb_ids(self) -> list[str]:
		"""
		Get spell kb_ids from localization table

		Queries for entries with kb_id matching 'spell_*'

		:return:
			List of unique spell kb_ids
		"""
		all_localizations = self._localization_repository.list_all()
		spell_kb_ids = []

		for loc in all_localizations:
			if loc.kb_id.startswith('spell_'):
				kb_id = loc.kb_id[6:]
				base_kb_id = self._extract_base_kb_id(kb_id)
				if base_kb_id and base_kb_id not in spell_kb_ids:
					spell_kb_ids.append(base_kb_id)

		return spell_kb_ids

	@staticmethod
	def _extract_base_kb_id(kb_id: str) -> str | None:
		"""
		Remove localization suffixes from kb_id

		:param kb_id:
			kb_id with possible suffix
		:return:
			Base kb_id without suffix, or None if invalid
		"""
		suffixes = ['_name', '_hint', '_desc', '_header', '_text_1', '_text_2', '_text_3']
		for suffix in suffixes:
			if kb_id.endswith(suffix):
				return kb_id[:-len(suffix)]
		return kb_id

	def _process_spell_data(
		self,
		kb_id: str,
		spell_data: dict
	) -> dict[str, Any] | None:
		"""
		Process single spell data

		Extracts: profit, price, school, levels (if present),
		scripted, params sections

		:param kb_id:
			Spell kb_id
		:param spell_data:
			Raw spell data from atom file
		:return:
			Processed spell dict or None if invalid
		"""
		if not isinstance(spell_data, dict):
			return None

		profit = spell_data.get('profit')
		price = spell_data.get('price')
		school = spell_data.get('school')

		if profit is None or price is None or school is None:
			return None

		mana_cost = None
		crystal_cost = None

		if 'levels' in spell_data and school in [1, 2, 3, 4]:
			levels = spell_data['levels']
			if isinstance(levels, (dict, list)):
				mana_cost, crystal_cost = self._parse_levels_block(levels)

		scripted = spell_data.get('scripted', {})
		params = spell_data.get('params', {})

		params = self._process_params(params)

		data = {
			'scripted': scripted,
			'params': params,
			'raw': spell_data
		}

		return {
			'kb_id': kb_id,
			'profit': profit,
			'price': price,
			'school': school,
			'mana_cost': mana_cost,
			'crystal_cost': crystal_cost,
			'data': data
		}

	def _parse_levels_block(self, levels: dict | list) -> tuple[list[int], list[int]]:
		"""
		Parse levels block into mana_cost and crystal_cost lists

		Format (dict): {1: "5,1", 2: "8,2", 3: "10,4"} or {"1": "5,1", "2": "8,2", "3": "10,4"}
		Format (list): ["5,1", "8,2", "10,4"]
		Returns: ([5, 8, 10], [1, 2, 4])

		:param levels:
			Levels dictionary or list from atom file
		:return:
			Tuple of (mana_costs, crystal_costs)
		"""
		mana_costs = []
		crystal_costs = []

		if isinstance(levels, list):
			for cost_str in levels:
				if isinstance(cost_str, str):
					parts = cost_str.split(',')
					if len(parts) == 2:
						mana_costs.append(int(parts[0].strip()))
						crystal_costs.append(int(parts[1].strip()))
		elif isinstance(levels, dict):
			sorted_keys = sorted(levels.keys(), key=lambda x: int(x) if isinstance(x, str) else x)

			for level in sorted_keys:
				level_num = int(level) if isinstance(level, str) else level
				if level_num > 0:
					cost_str = levels[level]
					if isinstance(cost_str, str):
						parts = cost_str.split(',')
						if len(parts) == 2:
							mana_costs.append(int(parts[0].strip()))
							crystal_costs.append(int(parts[1].strip()))

		return mana_costs, crystal_costs

	def _process_params(self, params: dict) -> dict:
		"""
		Process params dictionary: split comma-separated fields

		Fields to split: exception, target

		:param params:
			Parameters dictionary
		:return:
			Processed parameters dictionary
		"""
		processed = dict(params)

		fields_to_split = ['exception', 'target']
		for field in fields_to_split:
			if field in processed and isinstance(processed[field], str):
				processed[field] = self._split_comma_separated(processed[field])

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
