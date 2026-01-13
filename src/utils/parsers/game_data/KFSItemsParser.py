import typing
from logging import Logger

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.Item import Item
from src.domain.game.entities.Propbit import Propbit
from src.domain.exceptions import InvalidPropbitException
from src.utils.parsers import atom
from src.utils.parsers.game_data.IKFSReader import IKFSReader
from src.utils.parsers.game_data.IKFSItemsParser import IKFSItemsParser


class KFSItemsParser(IKFSItemsParser):

	def __init__(
		self,
		reader: IKFSReader = Provide[Container.kfs_reader],
		logger: Logger = Provide[Container.logger]
	):
		"""
		Initialize KFS items parser
		"""

		self._reader = reader
		self._logger = logger

	def parse(self, game_name: str) -> dict[str, list[Item]]:
		"""
		Extract and parse item data and set data from game files

		Reads all items*.txt files from extracted directories,
		parses sets and items, groups items by their set membership.
		Files are processed in order, with later files overwriting earlier ones.

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:return:
			Dictionary with sets as keys, each containing items list
			Also includes 'setless' key for items without sets
		"""
		items_contents = self._extract_files(game_name)

		# First pass: parse all set definitions (kb_id only)
		set_definitions = {}
		for items_content in items_contents:
			sets_from_file = self._parse_set_definitions(items_content)
			set_definitions.update(sets_from_file)

		# Second pass: parse all items into flat dictionary (later files overwrite earlier)
		all_items = {}
		for items_content in items_contents:
			items_data = self._parse_items_file(items_content)
			for kb_id, item_data in items_data.items():
				# Skip set definitions
				if kb_id.startswith('set_'):
					continue
				all_items[kb_id] = item_data

		# Third pass: build items and group by setref
		results = {}
		for set_kb_id in set_definitions.keys():
			results[set_kb_id] = []
		results["setless"] = []

		for kb_id, item_data in all_items.items():
			item = self._build_item(item_data)
			if item is not None:
				setref = item_data.get('setref', '')
				key = setref if setref and setref in results else "setless"
				results[key].append(item)

		self._logger.info(results)
		return results

	def _extract_files(self, game_name: str) -> list[str]:
		"""
		Read all items*.txt files from extracted data directory

		Uses glob pattern to dynamically discover all items files.

		:param game_name:
			Game name
		:return:
			List of items file contents
		"""
		return self._reader.read_data_files(game_name, ['items*.txt'])

	def _parse_items_file(self, content: str) -> dict[str, typing.Any]:
		"""
		Parse items.txt into list of item dictionaries using AtomParser

		:param content:
			Raw items.txt file content
		:return:
			List of dictionaries containing item data
		"""
		parsed = atom.loads(content)
		items = dict()

		for kb_id, block_data in parsed.items():
			if not isinstance(block_data, dict):
				continue

			item_data = {'kb_id': kb_id}

			for key in ['price', 'label', 'hint', 'propbits', 'setref', 'level']:
				if key in block_data:
					item_data[key] = block_data[key]

			if 'params' in block_data and isinstance(block_data['params'], dict):
				if 'upgrade' in block_data['params']:
					item_data['params_upgrade'] = block_data['params']['upgrade']

			items[kb_id] = item_data

		return items

	@staticmethod
	def _parse_propbits(propbits_str: str) -> list[Propbit]:
		"""
		Parse comma-separated propbits string into Propbit enum list

		:param propbits_str:
			Comma-separated string of propbit values
		:return:
			List of Propbit enum values
		:raises InvalidPropbitException:
			When any propbit value is invalid
		"""
		propbit_strings = [p.strip() for p in propbits_str.split(',')]
		result = []
		valid_values = [pb.value for pb in Propbit]

		for propbit_str in propbit_strings:
			try:
				result.append(Propbit(propbit_str))
			except ValueError as e:
				raise InvalidPropbitException(
					invalid_value=propbit_str,
					valid_values=valid_values,
					original_exception=e
				)

		return result

	def _build_item(self, item_data: dict[str, any]) -> Item | None:
		"""
		:param item_data:
			Dictionary containing parsed item data
		:return:
			Item entity with empty name and hint
		:raises InvalidPropbitException:
			When item_data contains invalid propbit values
		"""
		kb_id = item_data.get('kb_id', '')

		if not kb_id:
			return None

		price_str = item_data.get('price', '0')
		try:
			price = int(price_str)
		except ValueError:
			price = 0

		level_str = item_data.get('level', '1')
		try:
			level = int(level_str)
		except ValueError:
			level = 1

		propbits_str = item_data.get('propbits', '')
		propbits = None
		if propbits_str:
			propbits = self._parse_propbits(propbits_str)

		# Parse tiers from params.upgrade
		tiers = None
		params_upgrade = item_data.get('params_upgrade', "")
		if params_upgrade:
			# Split comma-separated kb_ids and strip whitespace
			tiers = [kb.strip() for kb in params_upgrade.split(',')]

		return Item(
			id=0,
			item_set_id=None,
			kb_id=kb_id,
			name='',
			price=price,
			hint=None,
			propbits=propbits,
			tiers=tiers,
			level=level
		)

	@staticmethod
	def _parse_set_definitions(content: str) -> dict[str, dict]:
		"""
		Parse set definitions from items.txt content

		:param content:
			Raw items.txt file content
		:return:
			Dictionary mapping set KB IDs to empty metadata
		"""
		sets = {}
		lines = content.split('\n')
		i = 0

		while i < len(lines):
			line = lines[i].strip()

			if line.startswith('set_') and '{' in line and not line.startswith('//'):
				parts = line.split('{', 1)
				kb_id = parts[0].strip()
				sets[kb_id] = {}

				# Skip to end of block
				brace_level = 1
				i += 1
				while i < len(lines) and brace_level > 0:
					line = lines[i].strip()
					brace_level += line.count('{')
					brace_level -= line.count('}')
					i += 1
				continue

			i += 1

		return sets
