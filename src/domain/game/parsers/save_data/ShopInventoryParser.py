from pathlib import Path
import struct
import re
from typing import Any, Optional

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.domain.game.parsers.save_data.IShopInventoryParser import IShopInventoryParser
from src.domain.game.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class ShopInventoryParser(IShopInventoryParser):

	METADATA_KEYWORDS: set[str] = {
		'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
		'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
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
		shop_positions = self._find_all_shop_ids(data)

		result = {}
		for shop_id, shop_pos in shop_positions:
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

		:param data:
			Decompressed save file data
		:return:
			List of (shop_id, position) tuples sorted by position
		"""
		shops = []
		pos = 0

		while pos < len(data):
			chunk_size = 10000
			if pos + chunk_size > len(data):
				chunk_size = len(data) - pos

			try:
				text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
				matches = re.finditer(r'itext_m_\w+_\d+', text)

				for match in matches:
					shop_id = match.group(0)
					shop_bytes = shop_id.encode('utf-16-le')
					actual_pos = data.find(shop_bytes, pos, pos+chunk_size)
					if actual_pos != -1 and shop_id not in [s[0] for s in shops]:
						shops.append((shop_id, actual_pos))
			except:
				pass

			pos += chunk_size

		return sorted(shops, key=lambda x: x[1])

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

				if 5 <= name_length <= 100:
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

				if 5 <= name_length <= 100:
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

		garrison_pos = self._find_preceding_section(data, b'.garrison', shop_pos, 5000)
		items_pos = self._find_preceding_section(data, b'.items', shop_pos, 5000)
		units_pos = self._find_preceding_section(data, b'.shopunits', shop_pos, 5000)
		spells_pos = self._find_preceding_section(data, b'.spells', shop_pos, 5000)

		if garrison_pos and items_pos:
			result['garrison'] = self._parse_slash_separated(data, garrison_pos, items_pos)

		if items_pos:
			next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
			result['items'] = self._parse_items_section(data, items_pos, next_pos)

		if units_pos:
			next_pos = spells_pos if spells_pos else shop_pos
			result['units'] = self._parse_slash_separated(data, units_pos, next_pos)

		if spells_pos:
			result['spells'] = self._parse_spells_section(data, spells_pos, shop_pos)

		return result

	def _is_valid_id(self, item_id: str) -> bool:
		"""
		Validate item/spell/unit ID

		:param item_id:
			ID string to validate
		:return:
			True if valid, False otherwise
		"""
		if not item_id or item_id in self.METADATA_KEYWORDS or len(item_id) < 5:
			return False
		return bool(re.match(r'^[a-z][a-z0-9_]*$', item_id))
