from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop
from src.domain.game.utils.KFSExtractor import KFSExtractor


class KFSLocationsAndShopsParser:

	def __init__(self, sessions_path: str, lang: str = 'rus', game_id: int = 0):
		"""
		Initialize KFS locations and shops parser

		:param sessions_path:
			Absolute path to sessions directory containing .kfs archives
		:param lang:
			Language code
		:param game_id:
			Game ID to associate with locations and shops
		"""
		self._sessions_path = sessions_path
		self._lang = lang
		self._game_id = game_id

	def parse(self) -> list[dict[str, Location | list[Shop]]]:
		"""
		Extract and parse location and shop data from game files

		Extracts atoms_info.lng from KFS archive, parses shop entries,
		and returns list of dictionaries containing Location entities
		and their associated Shop entities.

		:return:
			List of dictionaries with format:
			[{"location": Location(...), "shops": [Shop(...), ...]}, ...]
		"""
		localization_content = self._extract_files()
		shop_data = self._parse_localization(localization_content)
		return self._build_entities(shop_data)

	def _extract_files(self) -> str:
		"""
		Use KFSExtractor to get atoms_info.lng

		:return:
			Localization file content
		"""
		tables = [
			f"loc_ses{'_' + self._lang if self._lang != 'rus' else ''}.kfs/{self._lang}_atoms_info.lng"
		]

		extractor = KFSExtractor(self._sessions_path, tables)
		results = extractor.extract()
		return results[0]

	def _parse_localization(self, content: str) -> dict[str, dict[str, str]]:
		"""
		Parse atoms_info.lng into nested dictionary structure

		Groups shop entries by location_kb_id + shop_kb_id composite key.
		Only processes entries starting with 'itext_m_'.

		:param content:
			Raw localization file content
		:return:
			Dictionary mapping composite keys to field dictionaries
		"""
		localization: dict[str, dict[str, str]] = {}
		lines = content.split('\n')

		for line in lines:
			line = line.strip()
			if not line or line.startswith('//'):
				continue

			if '=' in line:
				key, value = line.split('=', 1)
				key = key.strip()
				value = value.strip()

				parsed = self._parse_shop_key(key)
				if parsed is not None:
					location_kb_id, shop_kb_id, field = parsed
					composite_key = f"{location_kb_id}_{shop_kb_id}"

					if composite_key not in localization:
						localization[composite_key] = {}

					localization[composite_key][f"_{field}"] = value

		return localization

	def _build_entities(
		self,
		shop_data: dict[str, dict[str, str]]
	) -> list[dict[str, Location | list[Shop]]]:
		"""
		Build Location and Shop entities from parsed data

		Extracts unique locations, creates location entities with id=0,
		and creates shop entities (also with id=0) grouped by location.

		:param shop_data:
			Nested dictionary of shop data from _parse_localization
		:return:
			List of dicts with "location" and "shops" keys
		"""
		# Group shops by location_kb_id
		locations_map: dict[str, dict] = {}

		for composite_key, fields in shop_data.items():
			# Validate: all 4 fields must be present
			required_fields = ['_hint', '_msg', '_name', '_terr']
			if not all(field in fields for field in required_fields):
				continue

			# Extract location_kb_id and shop_kb_id from composite key
			parts = composite_key.rsplit('_', 1)
			if len(parts) != 2:
				continue

			location_kb_id = parts[0]
			try:
				shop_kb_id = int(parts[1])
			except ValueError:
				continue

			# Strip ^?^ prefix from all values
			location_name = self._strip_prefix(fields['_terr'])
			shop_name = self._strip_prefix(fields['_name'])
			shop_hint = self._strip_prefix(fields['_hint'])
			shop_msg = self._strip_prefix(fields['_msg'])

			# Validate: location_name and shop_name must not be empty
			if not location_name or not shop_name:
				continue

			# Create or get location entry
			if location_kb_id not in locations_map:
				locations_map[location_kb_id] = {
					'location': Location(
						id=0,
						game_id=self._game_id,
						kb_id=location_kb_id,
						name=location_name
					),
					'shops': []
				}

			# Create shop entity
			shop = Shop(
				id=0,
				game_id=self._game_id,
				kb_id=shop_kb_id,
				location_id=0,
				name=shop_name,
				hint=shop_hint if shop_hint else None,
				msg=shop_msg if shop_msg else None
			)

			locations_map[location_kb_id]['shops'].append(shop)

		return list(locations_map.values())

	def _parse_shop_key(self, key: str) -> tuple[str, int, str] | None:
		"""
		Parse shop key into components

		:param key:
			Key like 'itext_m_portland_450_name'
		:return:
			Tuple of (location_kb_id, shop_kb_id, field) or None if invalid
		"""
		if not key.startswith('itext_m_'):
			return None

		# Remove prefix: 'portland_450_name'
		remainder = key[8:]  # Skip 'itext_m_'

		# Split by underscore
		parts = remainder.split('_')

		if len(parts) < 3:
			return None

		# Field is always last part
		field = parts[-1]

		# Find the shop_kb_id (last numeric part before field)
		shop_kb_id = None
		shop_kb_id_index = -1

		for i in range(len(parts) - 2, -1, -1):
			if parts[i].isdigit():
				shop_kb_id = int(parts[i])
				shop_kb_id_index = i
				break

		if shop_kb_id is None:
			return None

		# Everything before shop_kb_id is location_kb_id
		location_kb_id = '_'.join(parts[:shop_kb_id_index])

		if not location_kb_id:
			return None

		return (location_kb_id, shop_kb_id, field)

	def _strip_prefix(self, value: str) -> str:
		"""
		Strip ^?^ prefix from localization values

		:param value:
			Raw value from .lng file
		:return:
			Cleaned value without prefix
		"""
		if value.startswith('^?^'):
			return value[3:]
		return value
