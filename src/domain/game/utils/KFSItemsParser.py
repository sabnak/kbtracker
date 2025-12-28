from src.domain.game.entities.Item import Item
from src.domain.game.utils.KFSExtractor import KFSExtractor


class KFSItemsParser:

	def __init__(self, sessions_path: str, lang: str = 'rus'):
		"""
		Initialize KFS items parser

		:param sessions_path:
			Absolute path to sessions directory containing .kfs archives
		"""
		self._sessions_path = sessions_path
		self._lang = lang

	def parse(self) -> list[Item]:
		"""
		Extract and parse item data from game files

		Extracts items.txt and rus_items.lng from KFS archives,
		parses both files, and returns list of Item entities.

		:return:
			List of Item entities with populated fields
		"""
		items_content, localization_content = self._extract_files()
		localization = self._parse_localization(localization_content)
		item_data_list = self._parse_items_file(items_content)

		items = []
		for item_data in item_data_list:
			item = self._build_item_entity(item_data, localization)
			if item is not None:
				items.append(item)

		return items

	def _extract_files(self) -> tuple[str, str]:
		"""
		Use KFSExtractor to get items.txt and rus_items.lng

		:return:
			Tuple of (items_content, localization_content)
		"""
		tables = [
			"ses.kfs/items.txt",
			f"loc_ses{'_' + self._lang if self._lang != 'rus' else ''}.kfs/{self._lang}_items.lng"
		]

		extractor = KFSExtractor(self._sessions_path, tables)
		results = extractor.extract()
		return results[0], results[1]

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

				if key in ['price', 'label', 'hint', 'propbits']:
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

		propbits_str = item_data.get('propbits', '')
		propbits = None
		if propbits_str:
			propbits = [p.strip() for p in propbits_str.split(',')]

		return Item(
			id=0,
			kb_id=kb_id,
			name=name,
			price=price,
			hint=hint,
			propbits=propbits
		)
