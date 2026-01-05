from pathlib import Path
import struct
import re
from typing import Any, Optional

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.domain.exceptions import InvalidKbIdException, EntityNotFoundException
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.ISpellRepository import ISpellRepository
from src.domain.game.IUnitRepository import IUnitRepository
from src.domain.game.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.entities.ShopInventory import ShopInventory
from src.utils.parsers.save_data.IShopInventoryParser import IShopInventoryParser
from src.utils.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class ShopInventoryParser(IShopInventoryParser):

	METADATA_KEYWORDS: set[str] = {
		'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
		'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h', 'moral'
	}

	SECTION_MARKERS: set[bytes] = {
		b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp'
	}

	@inject
	def __init__(
		self,
		decompressor: ISaveFileDecompressor = Provide[Container.save_file_decompressor],
		item_repository: IItemRepository = Provide[Container.item_repository],
		spell_repository: ISpellRepository = Provide[Container.spell_repository],
		unit_repository: IUnitRepository = Provide[Container.unit_repository],
		shop_repository: IShopRepository = Provide[Container.shop_repository],
		shop_inventory_repository: IShopInventoryRepository = Provide[Container.shop_inventory_repository]
	):
		"""
		Initialize shop inventory parser

		:param decompressor:
			Save file decompressor
		:param item_repository:
			Item repository
		:param spell_repository:
			Spell repository
		:param unit_repository:
			Unit repository
		:param shop_repository:
			Shop repository
		:param shop_inventory_repository:
			Shop inventory repository
		"""
		self._decompressor = decompressor
		self._item_repository = item_repository
		self._spell_repository = spell_repository
		self._unit_repository = unit_repository
		self._shop_repository = shop_repository
		self._shop_inventory_repository = shop_inventory_repository

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

		Shop ID pattern: itext_{location}_{id}
		- location: can contain letters, numbers, underscores, hyphens
		  Examples: "m_portland", "aralan", "some-location"
		- id: numeric shop identifier

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
				matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

				for match in matches:
					shop_id_full = match.group(0)
					location = match.group(1)
					shop_num = match.group(2)
					shop_id = location + '_' + shop_num
					shop_bytes = shop_id_full.encode('utf-16-le')
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
			actual_end = self._find_section_end(data, items_pos, next_pos)
			result['items'] = self._parse_items_section(data, items_pos, actual_end)

		if units_pos:
			next_pos = spells_pos if spells_pos else shop_pos
			actual_end = self._find_section_end(data, units_pos, next_pos)
			result['units'] = self._parse_slash_separated(data, units_pos, actual_end)

		if spells_pos:
			actual_end = self._find_section_end(data, spells_pos, shop_pos)
			result['spells'] = self._parse_spells_section(data, spells_pos, actual_end)

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

	def sync(
		self,
		data: dict[str, dict[str, list[dict[str, Any]]]],
		profile_id: int
	) -> dict[str, int]:
		"""
		Sync parsed shop inventory data to database

		:param data:
			Parsed shop data from parse() method
		:param profile_id:
			Profile ID to associate inventories with
		:return:
			Dictionary with counts
		:raises EntityNotFoundException:
			If any shop, item, spell, or unit not found in database
		"""
		counts = {"items": 0, "spells": 0, "units": 0, "garrison": 0}

		for shop_kb_id, inventories in data.items():
			shop = self._shop_repository.get_by_kb_id(shop_kb_id)

			if not shop:
				raise EntityNotFoundException("Shop", shop_kb_id)

			counts["items"] += self._sync_items(inventories['items'], shop.id, profile_id)
			counts["spells"] += self._sync_spells(inventories['spells'], shop.id, profile_id)
			counts["units"] += self._sync_units(inventories['units'], shop.id, profile_id)
			counts["garrison"] += self._sync_garrison(inventories['garrison'], shop.id, profile_id)

		return counts

	def _sync_items(
		self,
		items: list[dict[str, Any]],
		shop_id: int,
		profile_id: int
	) -> int:
		"""
		Sync item inventories

		:param items:
			Item inventory data
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
			Number of items synced
		"""
		count = 0
		for item_data in items:
			kb_id = item_data['name']
			item = self._item_repository.get_by_kb_id(kb_id)

			if not item:
				raise EntityNotFoundException("Item", kb_id)

			inventory = ShopInventory(
				entity_id=item.id,
				shop_id=shop_id,
				profile_id=profile_id,
				type="item",
				count=item_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_spells(
		self,
		spells: list[dict[str, Any]],
		shop_id: int,
		profile_id: int
	) -> int:
		"""
		Sync spell inventories

		:param spells:
			Spell inventory data
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
			Number of spells synced
		"""
		count = 0
		for spell_data in spells:
			kb_id = spell_data['name']
			spell = self._spell_repository.get_by_kb_id(kb_id)

			if not spell:
				raise EntityNotFoundException("Spell", kb_id)

			inventory = ShopInventory(
				entity_id=spell.id,
				shop_id=shop_id,
				profile_id=profile_id,
				type="spell",
				count=spell_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_units(
		self,
		units: list[dict[str, Any]],
		shop_id: int,
		profile_id: int
	) -> int:
		"""
		Sync unit inventories

		:param units:
			Unit inventory data
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
			Number of units synced
		"""
		count = 0
		for unit_data in units:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				raise EntityNotFoundException("Unit", kb_id)

			inventory = ShopInventory(
				entity_id=unit.id,
				shop_id=shop_id,
				profile_id=profile_id,
				type="unit",
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count

	def _sync_garrison(
		self,
		garrison: list[dict[str, Any]],
		shop_id: int,
		profile_id: int
	) -> int:
		"""
		Sync garrison inventories

		:param garrison:
			Garrison inventory data
		:param shop_id:
			Shop ID
		:param profile_id:
			Profile ID
		:return:
			Number of garrison units synced
		"""
		count = 0
		for unit_data in garrison:
			kb_id = unit_data['name']
			unit = self._unit_repository.get_by_kb_id(kb_id)

			if not unit:
				raise EntityNotFoundException("Unit", kb_id)

			inventory = ShopInventory(
				entity_id=unit.id,
				shop_id=shop_id,
				profile_id=profile_id,
				type="garrison",
				count=unit_data['quantity']
			)
			self._shop_inventory_repository.create(inventory)
			count += 1

		return count
