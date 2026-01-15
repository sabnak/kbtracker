import re
import struct
from pathlib import Path
from typing import Any, Optional

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.utils.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor
from src.utils.parsers.save_data.IShopInventoryParser import IShopInventoryParser


class ShopInventoryParser(IShopInventoryParser):

	METADATA_KEYWORDS: set[str] = {
		'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
		'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h', 'moral',
		'mana', 'limit'
	}

	SECTION_MARKERS: set[bytes] = {
		b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp'
	}

	@inject
	def __init__(
		self,
		decompressor: ISaveFileDecompressor = Provide[Container.save_file_decompressor]
	):
		"""
		Initialize shop inventory parser

		:param decompressor:
			Save file decompressor
		"""
		self._decompressor = decompressor

	def parse(self, save_path: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
		"""
		Extract shop inventory data from save file

		Extracts all shops with 4 sections:
		- garrison: Player's stored army units
		- items: Equipment and consumables for sale
		- units: Units/troops for hire
		- spells: Spells for purchase

		Supports two shop types:
		1. itext_ shops: Standard named shops
		   Format: {location}_{shop_num}
		   Example: m_portland_8671

		2. building_trader@ shops: Shops without itext_ identifiers
		   Actor IDs are extracted from .actors section's 'strg' field
		   by clearing bit 7 of the last byte

		   Format with actor: {location}_actor_{actor_id}
		   Example: dragondor_actor_807991996
		   (actor_id maps to actor_system_{id}_name in localization)

		   Format without actor: {location}_building_trader_{building_num}
		   Example: m_inselburg_building_trader_31
		   (inactive shops or shops without assigned traders)

		:param save_path:
			Path to save 'data' file
		:return:
			Dictionary mapping shop_id to inventory sections
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		data = self._decompressor.decompress(save_path)

		itext_shops = self._find_all_shop_ids(data)
		building_shops = self._find_building_trader_shops(data)

		all_shops = itext_shops + building_shops
		all_shops = sorted(all_shops, key=lambda x: x[1])

		result = {}
		for shop_id, shop_pos in all_shops:
			shop_data = self._parse_shop(data, shop_id, shop_pos)
			result[shop_id] = {
				'garrison': [{'name': n, 'quantity': q} for n, q in shop_data['garrison']],
				'items': [{'name': n, 'quantity': q} for n, q in shop_data['items']],
				'units': [{'name': n, 'quantity': q} for n, q in shop_data['units']],
				'spells': [{'name': n, 'quantity': q} for n, q in shop_data['spells']]
			}

		return result

	def _find_all_shop_ids(self, data: bytes) -> list[tuple[str, int]]:
		"""
		Find all shop IDs in save file

		Shop ID pattern: itext_{location}_{id}
		- location: can contain letters, numbers, underscores, hyphens
		  Examples: "m_portland", "aralan", "some-location"
		- id: numeric shop identifier

		Uses overlapping chunks to prevent shop IDs from being split
		across chunk boundaries. Deduplicates using both position and
		shop_id to prevent multiple occurrences of the same shop.

		:param data:
			Decompressed save file data
		:return:
			List of (shop_id, position) tuples sorted by position
		"""
		shops = []
		seen_positions = set()
		seen_shop_ids = set()
		pos = 0
		chunk_size = 10000
		overlap = 200

		while pos < len(data):
			current_chunk_size = min(chunk_size, len(data) - pos)

			try:
				text = data[pos:pos+current_chunk_size].decode('utf-16-le', errors='ignore')
				matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

				for match in matches:
					shop_id_full = match.group(0)
					location = match.group(1)
					shop_num = match.group(2)
					shop_id = location + '_' + shop_num
					shop_bytes = shop_id_full.encode('utf-16-le')
					actual_pos = data.find(shop_bytes, pos, pos+current_chunk_size)
					if actual_pos != -1 and actual_pos not in seen_positions and shop_id not in seen_shop_ids:
						shops.append((shop_id, actual_pos))
						seen_positions.add(actual_pos)
						seen_shop_ids.add(shop_id)
			except:
				pass

			pos += chunk_size - overlap

		return sorted(shops, key=lambda x: x[1])

	def _extract_actor_id_from_actors_section(
		self,
		data: bytes,
		building_pos: int
	) -> Optional[int]:
		"""
		Extract actor ID from .actors section before building_trader@

		Structure: .actors section contains a 'strg' field with encoded actor ID
		The actor ID is stored with bit 7 set in the last byte:
		- If bit 7 is SET: Shop is active, actor ID extracted by clearing bit 7
		- If bit 7 is NOT SET: Shop is inactive/template, no valid actor ID

		Example:
		strg value: 0xb028fabc (bytes: bc fa 28 b0)
		actor_id:   0x3028fabc (bytes: bc fa 28 30)
		Difference: Last byte 0xb0 → 0x30 (bit 7 cleared)

		:param data:
			Decompressed save file data
		:param building_pos:
			Position of building_trader@ marker
		:return:
			Actor ID or None if not found or inactive shop
		"""
		search_start = max(0, building_pos - 3000)
		search_chunk = data[search_start:building_pos]

		actors_pos = search_chunk.rfind(b'.actors')
		if actors_pos == -1:
			return None

		abs_actors_pos = search_start + actors_pos
		chunk = data[abs_actors_pos:abs_actors_pos + 100]

		strg_pos = chunk.find(b'strg')
		if strg_pos == -1:
			return None

		value_offset = strg_pos + 8
		if value_offset + 4 > len(chunk):
			return None

		try:
			strg_value = struct.unpack('<I', chunk[value_offset:value_offset + 4])[0]

			strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))

			if (strg_bytes[3] & 0x80) == 0:
				return None

			actor_bytes = list(strg_bytes)
			actor_bytes[3] = actor_bytes[3] & 0x7F

			actor_id = struct.unpack('<I', bytes(actor_bytes))[0]

			return actor_id

		except:
			return None

	def _find_building_trader_shops(self, data: bytes) -> list[tuple[str, int]]:
		"""
		Find all building_trader@ shops without itext_ identifiers

		Structure: .actors → .shopunits → .spells → .temp → lt <location> → building_trader@<id>

		Shop ID format:
		- If actor ID extracted from .actors: {location}_actor_{actor_id}
		- If no actor ID found: {location}_building_trader_{building_num}

		Actor ID extraction:
		- Extracted from .actors section's 'strg' field by clearing bit 7
		- Only shops with bit 7 set are active and have assigned actors
		- Shops without bit 7 set are inactive/template shops

		Unnamed shops without actor IDs typically:
		- Have no name in game
		- Do not display on game map
		- Are still fully interactable with inventory

		:param data:
			Decompressed save file data
		:return:
			List of (shop_id, position) tuples
		"""
		shops = []
		seen_inventory_positions = set()
		pos = 0

		while pos < len(data):
			pos = data.find(b'building_trader@', pos)
			if pos == -1:
				break

			segment = data[pos:pos+30]
			try:
				text = segment.decode('ascii', errors='ignore')
				match = re.match(r'building_trader@(\d+)', text)
				if match:
					building_num = match.group(1)

					location = self._extract_location_from_lt_tag(data, pos)

					if location:
						shopunits_pos = self._find_preceding_section(data, b'.shopunits', pos, 2000)

						if shopunits_pos and self._section_belongs_to_building_trader(
							data, shopunits_pos, pos
						):
							if shopunits_pos not in seen_inventory_positions:
								actor_id = self._extract_actor_id_from_actors_section(data, pos)
								if actor_id:
									shop_id = f'{location}_actor_{actor_id}'
								else:
									shop_id = f'{location}_building_trader_{building_num}'

								shops.append((shop_id, pos))
								seen_inventory_positions.add(shopunits_pos)
			except:
				pass

			pos += 1

		return shops

	def _extract_location_from_lt_tag(
		self,
		data: bytes,
		building_pos: int
	) -> Optional[str]:
		"""
		Extract location from 'lt' tag before building_trader@

		Structure: lt [4-byte length] [location_name]
		Typically appears ~29 bytes before building_trader@

		:param data:
			Save file data
		:param building_pos:
			Position of building_trader@
		:return:
			Location name or None if not found
		"""
		search_start = max(0, building_pos - 500)
		chunk = data[search_start:building_pos]

		lt_pos = chunk.rfind(b'lt')

		if lt_pos != -1:
			abs_lt_pos = search_start + lt_pos

			if abs_lt_pos + 6 < len(data):
				try:
					length_bytes = data[abs_lt_pos + 2:abs_lt_pos + 6]
					location_length = struct.unpack('<I', length_bytes)[0]

					if 0 < location_length < 100:
						location_start = abs_lt_pos + 6
						location_bytes = data[location_start:location_start + location_length]
						location = location_bytes.decode('ascii')
						return location
				except:
					pass

		return None

	def _section_belongs_to_building_trader(
		self,
		data: bytes,
		section_pos: int,
		building_pos: int
	) -> bool:
		"""
		Verify that no other shop ID exists between section and building_trader@

		:param data:
			Save file data
		:param section_pos:
			Section position
		:param building_pos:
			building_trader@ position
		:return:
			True if section belongs to this building_trader
		"""
		chunk = data[section_pos:building_pos]

		if b'itext_' in chunk:
			return False

		if b'building_trader@' in chunk:
			return False

		return True

	def _find_preceding_section(
		self,
		data: bytes,
		marker: bytes,
		shop_pos: int,
		max_distance: int = 5000
	) -> Optional[int]:
		"""
		Find section marker immediately before shop ID

		:param data:
			Save file data
		:param marker:
			Section marker
		:param shop_pos:
			Shop ID position
		:param max_distance:
			Maximum distance to search backwards
		:return:
			Section position or None if not found
		"""
		search_start = max(0, shop_pos - max_distance)
		chunk = data[search_start:shop_pos]
		last_pos = chunk.rfind(marker)

		if last_pos != -1:
			return search_start + last_pos
		return None

	def _find_section_end(
		self,
		data: bytes,
		section_start: int,
		max_end: int
	) -> int:
		"""
		Find actual end of section by detecting next section marker

		Prevents parsing beyond section boundaries into adjacent sections
		like .temp, which can contain data that matches entry patterns
		but isn't part of the current section.

		:param data:
			Save file data
		:param section_start:
			Starting position of current section
		:param max_end:
			Maximum possible end (usually shop ID position)
		:return:
			Actual end position of section
		"""
		search_area = data[section_start:max_end]
		earliest_marker_pos = max_end

		for marker in self.SECTION_MARKERS:
			pos = search_area.find(marker, 1)
			if pos != -1:
				absolute_pos = section_start + pos
				earliest_marker_pos = min(earliest_marker_pos, absolute_pos)

		return earliest_marker_pos

	def _parse_slash_separated(
		self,
		data: bytes,
		section_pos: int,
		next_pos: int
	) -> list[tuple[str, int]]:
		"""
		Parse slash-separated format

		:param data:
			Save file data
		:param section_pos:
			Section start position
		:param next_pos:
			Next section/shop position
		:return:
			List of (name, quantity) tuples
		"""
		pos = section_pos

		strg_pos = data.find(b'strg', pos, next_pos)
		if strg_pos == -1:
			return []

		pos = strg_pos + 4

		if pos + 4 > len(data):
			return []

		str_length = struct.unpack('<I', data[pos:pos+4])[0]
		pos += 4

		if str_length <= 0 or str_length > 5000:
			return []

		if pos + str_length > len(data):
			return []

		try:
			content_str = data[pos:pos+str_length].decode('ascii')
			parts = content_str.split('/')

			items = []
			i = 0
			while i < len(parts) - 1:
				name = parts[i]
				try:
					quantity = int(parts[i + 1])
					if self._is_valid_id(name):
						items.append((name, quantity))
					i += 2
				except:
					i += 1

			return items

		except:
			return []

	def _parse_items_section(
		self,
		data: bytes,
		section_pos: int,
		next_pos: int
	) -> list[tuple[str, int]]:
		"""
		Parse items section

		:param data:
			Save file data
		:param section_pos:
			Section start position
		:param next_pos:
			Next section/shop position
		:return:
			List of (name, quantity) tuples
		"""
		items = []
		pos = section_pos + len(b'.items')
		search_end = next_pos

		while pos < search_end - 20:
			if pos + 4 > len(data):
				break

			try:
				name_length = struct.unpack('<I', data[pos:pos+4])[0]

				if 3 <= name_length <= 100:
					if pos + 4 + name_length > len(data):
						pos += 1
						continue

					try:
						name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

						if self._is_valid_id(name):
							scan_pos = pos + 4 + name_length
							quantity = 1

							for _ in range(125):
								if scan_pos + 10 > search_end:
									break

								if data[scan_pos:scan_pos+6] == b'slruck':
									try:
										val_len = struct.unpack('<I', data[scan_pos+6:scan_pos+10])[0]
										if 1 <= val_len <= 20:
											val_str = data[scan_pos+10:scan_pos+10+val_len].decode('ascii', errors='strict')
											if ',' in val_str:
												parts = val_str.split(',')
												if len(parts) == 2:
													quantity = int(parts[1])
													break
									except:
										pass

								scan_pos += 1

							items.append((name, quantity))
							pos += 4 + name_length
							continue

					except:
						pass
			except:
				pass

			pos += 1

		return sorted(items)

	def _parse_spells_section(
		self,
		data: bytes,
		section_pos: int,
		next_pos: int
	) -> list[tuple[str, int]]:
		"""
		Parse spells section

		:param data:
			Save file data
		:param section_pos:
			Section start position
		:param next_pos:
			Next section/shop position
		:return:
			List of (name, quantity) tuples
		"""
		spells_dict = {}
		pos = section_pos + len(b'.spells')
		search_end = next_pos

		while pos < search_end - 20:
			if pos + 4 > len(data):
				break

			try:
				name_length = struct.unpack('<I', data[pos:pos+4])[0]

				if 3 <= name_length <= 100:
					if pos + 4 + name_length + 4 > len(data):
						pos += 1
						continue

					try:
						name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

						if self._is_valid_id(name):
							quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

							if 0 < quantity < 10000:
								if name not in spells_dict or spells_dict[name] < quantity:
									spells_dict[name] = quantity

								pos += 4 + name_length + 4
								continue

					except:
						pass
			except:
				pass

			pos += 1

		return sorted(spells_dict.items())

	def _section_belongs_to_shop(
		self,
		data: bytes,
		section_pos: int,
		shop_pos: int
	) -> bool:
		"""
		Verify that no other shop ID exists between section and shop

		Prevents attributing sections to wrong shop when searching backwards
		across shop boundaries.

		:param data:
			Save file data
		:param section_pos:
			Section position
		:param shop_pos:
			Shop ID position
		:return:
			True if section belongs to this shop
		"""
		chunk = data[section_pos:shop_pos]

		try:
			text = chunk.decode('utf-16-le', errors='ignore')
			if re.search(r'itext_[-\w]+_\d+', text):
				return False
		except:
			pass

		return True

	def _parse_shop(self, data: bytes, shop_id: str, shop_pos: int) -> dict:
		"""
		Parse complete shop with all 4 sections

		:param data:
			Save file data
		:param shop_id:
			Shop identifier
		:param shop_pos:
			Shop ID position
		:return:
			Dictionary with shop data
		"""
		result = {
			'shop_id': shop_id,
			'garrison': [],
			'items': [],
			'units': [],
			'spells': []
		}

		sections = {}
		for marker, key in [
			(b'.garrison', 'garrison'),
			(b'.items', 'items'),
			(b'.shopunits', 'units'),
			(b'.spells', 'spells')
		]:
			pos = self._find_preceding_section(data, marker, shop_pos, 5000)
			if pos and self._section_belongs_to_shop(data, pos, shop_pos):
				sections[key] = {'marker': marker, 'pos': pos}

		sorted_sections = sorted(sections.items(), key=lambda x: x[1]['pos'])

		for i, (key, section_info) in enumerate(sorted_sections):
			section_pos = section_info['pos']
			marker = section_info['marker']

			if i + 1 < len(sorted_sections):
				next_boundary = sorted_sections[i + 1][1]['pos']
			else:
				next_boundary = shop_pos

			actual_end = self._find_section_end(data, section_pos, next_boundary)

			if marker == b'.garrison':
				if i + 1 < len(sorted_sections):
					next_section_pos = sorted_sections[i + 1][1]['pos']
					result['garrison'] = self._parse_slash_separated(
						data,
						section_pos,
						next_section_pos
					)
			elif marker == b'.items':
				result['items'] = self._parse_items_section(data, section_pos, actual_end)
			elif marker == b'.shopunits':
				result['units'] = self._parse_slash_separated(data, section_pos, actual_end)
			elif marker == b'.spells':
				result['spells'] = self._parse_spells_section(data, section_pos, actual_end)

		return result

	def _is_valid_id(self, item_id: str) -> bool:
		"""
		Validate item/spell/unit ID

		:param item_id:
			ID string to validate
		:return:
			True if valid, False otherwise
		"""
		if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 3:
			return False
		return bool(re.match(r'^[a-z][a-z0-9_]*$', item_id))
