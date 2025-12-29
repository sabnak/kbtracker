import os
import zipfile

from src.domain.game.entities.Item import Item
from src.domain.game.utils.KFSExtractor import KFSExtractor


class KFSItemsParser:

	def __init__(self, sessions_path: str, lang: str = 'rus', game_id: int = 0):
		"""
		Initialize KFS items parser

		:param sessions_path:
			Absolute path to sessions directory containing .kfs archives
		:param lang:
			Language code
		:param game_id:
			Game ID to associate with items
		"""
		self._sessions_path = sessions_path
		self._lang = lang
		self._game_id = game_id

	def parse(self) -> dict[str, dict[str, any]]:
		"""
		Extract and parse item data and set data from game files

		Extracts all items*.txt files and localization file from KFS archives,
		parses sets and items, groups items by their set membership.

		:return:
			Dictionary with sets as keys, each containing name, hint, and items list
			Also includes 'setless' key for items without sets
		"""
		items_contents, localization_content = self._extract_files()
		localization = self._parse_localization(localization_content)

		# First pass: parse all set definitions
		set_definitions = {}
		for items_content in items_contents:
			sets_from_file = self._parse_set_definitions(items_content, localization)
			set_definitions.update(sets_from_file)

		# Initialize results with all known sets
		results = {}
		for set_kb_id, set_metadata in set_definitions.items():
			results[set_kb_id] = {
				"name": set_metadata["name"],
				"hint": set_metadata["hint"],
				"items": []
			}
		results["setless"] = {"items": []}

		# Second pass: parse all items and group by setref
		for items_content in items_contents:
			items_by_set = self._parse_items_grouped_by_set(items_content, localization)
			for set_kb_id, items in items_by_set.items():
				if set_kb_id in results:
					results[set_kb_id]["items"].extend(items)
				else:
					results["setless"]["items"].extend(items)

		return results

	def _extract_files(self) -> tuple[list[str], str]:
		"""
		Use KFSExtractor to get all items*.txt files and localization file

		:return:
			Tuple of (list of items_contents, localization_content)
		"""
		items_files = self._discover_items_files()
		localization_file = f"loc_ses{'_' + self._lang if self._lang != 'rus' else ''}.kfs/{self._lang}_items.lng"

		tables = items_files + [localization_file]

		extractor = KFSExtractor(self._sessions_path, tables)
		results = extractor.extract()

		items_contents = results[:-1]
		localization_content = results[-1]

		return items_contents, localization_content

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

	def _parse_localization(self, content: str) -> dict[str, str]:
		"""
		Parse rus_items.lng into key-value dictionary

		:param content:
			Raw localization file content
		:return:
			Dictionary mapping localization keys to values
		"""
		localization: dict[str, str] = {}
		lines = content.split('\n')

		for line in lines:
			line = line.strip()
			if not line or line.startswith('//'):
				continue

			if '=' in line:
				key, value = line.split('=', 1)
				key = key.strip()
				value = value.strip()

				if key.startswith('itm_'):
					localization[key] = value

		return localization

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

	def _build_item_entity(
		self,
		item_data: dict[str, any],
		localization: dict[str, str]
	) -> Item | None:
		"""
		Build Item entity from parsed data and localization

		:param item_data:
			Dictionary containing parsed item data
		:param localization:
			Dictionary of localization strings
		:return:
			Item entity or None if name lookup fails
		"""
		kb_id = item_data.get('kb_id', '')
		label = item_data.get('label', '')
		hint_key = item_data.get('hint', '')

		name = localization.get(label, '')
		if not name:
			return None

		hint = localization.get(hint_key, None) if hint_key else None

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
			propbits = [p.strip() for p in propbits_str.split(',')]

		return Item(
			id=0,
			game_id=self._game_id,
			item_set_id=None,
			kb_id=kb_id,
			name=name,
			price=price,
			hint=hint,
			propbits=propbits,
			level=level
		)

	def _parse_set_definitions(
		self,
		content: str,
		localization: dict[str, str]
	) -> dict[str, dict[str, str | None]]:
		"""
		Parse set definitions from items.txt content

		:param content:
			Raw items.txt file content
		:param localization:
			Dictionary of localization strings
		:return:
			Dictionary mapping set KB IDs to their metadata (name, hint)
		"""
		sets = {}
		lines = content.split('\n')
		i = 0

		while i < len(lines):
			line = lines[i].strip()

			if line.startswith('set_') and '{' in line and not line.startswith('//'):
				parts = line.split('{', 1)
				kb_id = parts[0].strip()

				set_data, end_idx = self._parse_set_block(lines, i)
				if set_data:
					metadata = self._build_set_metadata(kb_id, set_data, localization)
					if metadata:
						sets[kb_id] = metadata
				i = end_idx
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

	def _build_set_metadata(
		self,
		kb_id: str,
		set_data: dict[str, str],
		localization: dict[str, str]
	) -> dict[str, str | None] | None:
		"""
		Build set metadata from parsed data and localization

		:param kb_id:
			Set identifier (e.g., 'set_knight')
		:param set_data:
			Dictionary containing parsed set data
		:param localization:
			Dictionary of localization strings
		:return:
			Dictionary with name and hint, or None if name lookup fails
		"""
		label = set_data.get('label', '')
		hint_key = set_data.get('hint', '')

		name = localization.get(label, '')
		if not name:
			return None

		hint = localization.get(hint_key, None) if hint_key else None

		return {"name": name, "hint": hint}

	def _parse_items_grouped_by_set(
		self,
		content: str,
		localization: dict[str, str]
	) -> dict[str, list[Item]]:
		"""
		Parse items from content and group by setref

		:param content:
			Raw items.txt file content
		:param localization:
			Dictionary of localization strings
		:return:
			Dictionary mapping set KB IDs to lists of items
		"""
		items_by_set = {}
		item_data_list = self._parse_items_file(content)

		for item_data in item_data_list:
			# Skip set definitions (they start with set_)
			kb_id = item_data.get('kb_id', '')
			if kb_id.startswith('set_'):
				continue

			item = self._build_item_entity(item_data, localization)
			if item is not None:
				setref = item_data.get('setref', '')
				set_key = setref if setref else 'setless'

				if set_key not in items_by_set:
					items_by_set[set_key] = []

				items_by_set[set_key].append(item)

		return items_by_set
