import os
import zipfile

from src.domain.game.entities.Item import Item
from src.domain.game.entities.Propbit import Propbit
from src.domain.game.utils.KFSExtractor import KFSExtractor
from src.domain.exceptions import InvalidPropbitException


class KFSItemsParser:

	def __init__(self, sessions_path: str):
		"""
		Initialize KFS items parser

		:param sessions_path:
			Absolute path to sessions directory containing .kfs archives
		"""
		self._sessions_path = sessions_path

	def parse(self) -> dict[str, dict[str, any]]:
		"""
		Extract and parse item data and set data from game files

		Extracts all items*.txt files from KFS archives,
		parses sets and items, groups items by their set membership.

		Note: name and hint fields are NOT populated - they come from localization table

		:return:
			Dictionary with sets as keys, each containing items list
			Also includes 'setless' key for items without sets
		"""
		items_contents = self._extract_files()

		# First pass: parse all set definitions (kb_id only)
		set_definitions = {}
		for items_content in items_contents:
			sets_from_file = self._parse_set_definitions(items_content)
			set_definitions.update(sets_from_file)

		# Initialize results with all known sets
		results = {}
		for set_kb_id in set_definitions.keys():
			results[set_kb_id] = {"items": []}
		results["setless"] = {"items": []}

		# Second pass: parse all items and group by setref
		for items_content in items_contents:
			items_by_set = self._parse_items_grouped_by_set(items_content)
			for set_kb_id, items in items_by_set.items():
				if set_kb_id in results:
					results[set_kb_id]["items"].extend(items)
				else:
					results["setless"]["items"].extend(items)

		return results

	def _extract_files(self) -> list[str]:
		"""
		Use KFSExtractor to get all items*.txt files

		:return:
			List of items file contents
		"""
		items_files = self._discover_items_files()

		extractor = KFSExtractor(self._sessions_path, items_files)
		results = extractor.extract()

		return results

	def _discover_items_files(self) -> list[str]:
		"""
		Discover all items*.txt files in ses.kfs archive

		:return:
			List of file paths in format 'ses.kfs/items*.txt'
		:raises FileNotFoundError:
			If ses.kfs archive not found
		"""
		ses_archive_path = self._find_ses_archive()
		items_files = []

		with zipfile.ZipFile(ses_archive_path, 'r') as archive:
			for file_name in archive.namelist():
				if file_name.startswith('items') and file_name.endswith('.txt'):
					items_files.append(f"ses.kfs/{file_name}")

		return sorted(items_files)

	def _find_ses_archive(self) -> str:
		"""
		Find ses.kfs archive in sessions directory

		:return:
			Full path to ses.kfs archive
		:raises FileNotFoundError:
			If sessions directory or ses.kfs archive not found
		"""
		if not os.path.exists(self._sessions_path):
			raise FileNotFoundError(
				f"Sessions directory not found: {self._sessions_path}"
			)

		for entry in os.listdir(self._sessions_path):
			entry_path = os.path.join(self._sessions_path, entry)
			if os.path.isdir(entry_path):
				ses_archive = os.path.join(entry_path, "ses.kfs")
				if os.path.exists(ses_archive):
					return ses_archive

		raise FileNotFoundError(
			f"Archive 'ses.kfs' not found in {self._sessions_path}"
		)

	def _parse_items_file(self, content: str) -> list[dict[str, any]]:
		"""
		Parse items.txt into list of item dictionaries

		:param content:
			Raw items.txt file content
		:return:
			List of dictionaries containing item data
		"""
		items = []
		lines = content.split('\n')
		i = 0

		while i < len(lines):
			line = lines[i].strip()

			if '{' in line and not line.startswith('//'):
				parts = line.split('{', 1)
				potential_kb_id = parts[0].strip()

				if potential_kb_id and not any(c in potential_kb_id for c in ['=', ' ']):
					item_data, end_idx = self._parse_item_block(lines, i)
					if item_data:
						items.append(item_data)
					i = end_idx
					continue

			i += 1

		return items

	def _parse_item_block(
		self,
		lines: list[str],
		start_idx: int
	) -> tuple[dict[str, any] | None, int]:
		"""
		Parse single item block from lines

		:param lines:
			All lines from items.txt
		:param start_idx:
			Index of line containing item identifier
		:return:
			Tuple of (item_data dict or None, end_index)
		"""
		line = lines[start_idx].strip()
		parts = line.split('{', 1)
		kb_id = parts[0].strip()

		item_data = {'kb_id': kb_id}
		brace_level = 1
		i = start_idx + 1

		while i < len(lines) and brace_level > 0:
			line = lines[i].strip()

			brace_level += line.count('{')
			brace_level -= line.count('}')

			if brace_level == 1 and '=' in line and not line.startswith('//'):
				key, value = line.split('=', 1)
				key = key.strip()
				value = value.strip()

				if key in ['price', 'label', 'hint', 'propbits', 'setref', 'level']:
					item_data[key] = value

			i += 1

		return item_data, i

	def _parse_propbits(self, propbits_str: str) -> list[Propbit]:
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

	def _build_item_without_localization(self, item_data: dict[str, any]) -> Item | None:
		"""
		Build Item entity from parsed data WITHOUT localization

		Name and hint will be populated from database via localization JOINs

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

		# Name and hint are empty - will be populated from localization table
		return Item(
			id=0,
			item_set_id=None,
			kb_id=kb_id,
			name='',
			price=price,
			hint=None,
			propbits=propbits,
			level=level
		)

	def _parse_set_definitions(self, content: str) -> dict[str, dict]:
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

	def _parse_set_block(
		self,
		lines: list[str],
		start_idx: int
	) -> tuple[dict[str, str] | None, int]:
		"""
		Parse single set block from lines

		:param lines:
			All lines from items.txt
		:param start_idx:
			Index of line containing set identifier
		:return:
			Tuple of (set_data dict or None, end_index)
		"""
		set_data = {}
		brace_level = 1
		i = start_idx + 1

		while i < len(lines) and brace_level > 0:
			line = lines[i].strip()

			brace_level += line.count('{')
			brace_level -= line.count('}')

			if brace_level == 1 and '=' in line and not line.startswith('//'):
				key, value = line.split('=', 1)
				key = key.strip()
				value = value.strip()

				if key in ['label', 'hint']:
					set_data[key] = value

			i += 1

		return set_data, i

	def _parse_items_grouped_by_set(self, content: str) -> dict[str, list[Item]]:
		"""
		Parse items from content and group by setref

		Note: name and hint are NOT populated - they come from localization

		:param content:
			Raw items.txt file content
		:return:
			Dictionary mapping set KB IDs to lists of items
		"""
		items_by_set = {}
		item_data_list = self._parse_items_file(content)

		for item_data in item_data_list:
			# Skip set definitions
			kb_id = item_data.get('kb_id', '')
			if kb_id.startswith('set_'):
				continue

			item = self._build_item_without_localization(item_data)
			if item is not None:
				setref = item_data.get('setref', '')
				set_key = setref if setref else 'setless'

				if set_key not in items_by_set:
					items_by_set[set_key] = []

				items_by_set[set_key].append(item)

		return items_by_set
