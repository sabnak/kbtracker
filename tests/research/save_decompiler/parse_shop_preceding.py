#!/usr/bin/env python3
"""
Parse shop using sections immediately PRECEDING the shop ID
"""
import struct
import re
import os


def is_valid_id(item_id: str) -> bool:
	"""Validate item/spell/unit ID"""
	if not item_id:
		return False
	pattern = r'^[a-z][a-z0-9_]*$'
	return bool(re.match(pattern, item_id))


def find_shop_section(data: bytes, shop_id: str) -> int:
	"""Find shop position by ID"""
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)
	return pos if pos != -1 else None


def find_preceding_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 5000) -> int:
	"""Find section marker immediately BEFORE shop ID (within max_distance)"""
	search_start = max(0, shop_pos - max_distance)

	# Find last occurrence of marker before shop_pos
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos

	return None


def parse_section_with_quantities(data: bytes, section_pos: int, marker_len: int) -> list:
	"""Parse section with quantities"""
	results = []
	pos = section_pos + marker_len

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4

	# Read count
	if pos + 4 > len(data):
		return []

	item_count = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4
	pos += 8  # Skip metadata

	# Parse entries
	for i in range(min(item_count + 10, 150)):
		if pos + 4 > len(data):
			break

		# Read name length
		name_length = struct.unpack('<I', data[pos:pos+4])[0]
		pos += 4

		if name_length <= 0 or name_length > 200:
			break

		if pos + name_length > len(data):
			break

		# Read name
		try:
			name = data[pos:pos+name_length].decode('ascii', errors='strict')
			pos += name_length

			# Read quantity
			if pos + 4 <= len(data):
				quantity = struct.unpack('<I', data[pos:pos+4])[0]
			else:
				quantity = 1

			# Validate and add
			if is_valid_id(name) and quantity > 0 and quantity < 10000:
				results.append((name, quantity))

			# Find next entry
			max_skip = 200
			found_next = False
			for skip in range(max_skip):
				if pos + skip + 4 > len(data):
					break

				next_len = struct.unpack('<I', data[pos+skip:pos+skip+4])[0]
				if 5 <= next_len <= 100:
					try:
						test_name = data[pos+skip+4:pos+skip+4+min(next_len, 50)].decode('ascii', errors='strict')
						if '_' in test_name and test_name[0].isalpha():
							pos += skip
							found_next = True
							break
					except:
						pass

			if not found_next:
				break

		except:
			break

	return results


def parse_shop_preceding(data: bytes, shop_id: str) -> dict:
	"""Parse shop using sections immediately BEFORE shop ID"""
	shop_pos = find_shop_section(data, shop_id)
	if shop_pos is None:
		return None

	result = {
		'items': [],
		'spells': [],
		'units': []
	}

	print(f"\nShop at offset: {shop_pos} (0x{shop_pos:X})")

	# Find PRECEDING sections (within 5KB before shop ID)
	items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
	if items_pos:
		distance = shop_pos - items_pos
		print(f"Preceding .items at -{distance} bytes (offset {items_pos})")
		items = parse_section_with_quantities(data, items_pos, len(b'.items'))
		result['items'] = items
		print(f"  Parsed {len(items)} items")

	spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)
	if spells_pos:
		distance = shop_pos - spells_pos
		print(f"Preceding .spells at -{distance} bytes (offset {spells_pos})")
		spells = parse_section_with_quantities(data, spells_pos, len(b'.spells'))
		result['spells'] = spells
		print(f"  Parsed {len(spells)} spells")

	units_pos = find_preceding_section(data, b'.shopunits', shop_pos, 5000)
	if units_pos:
		distance = shop_pos - units_pos
		print(f"Preceding .shopunits at -{distance} bytes (offset {units_pos})")
		units = parse_section_with_quantities(data, units_pos, len(b'.shopunits'))
		result['units'] = units
		print(f"  Parsed {len(units)} units")

	return result


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	shop_id = 'itext_m_zcom_1422'
	print(f"{'='*78}")
	print(f"Parsing shop (PRECEDING sections): {shop_id}")
	print(f"{'='*78}")

	shop_data = parse_shop_preceding(data, shop_id)

	if shop_data:
		print(f"\n{'='*78}")
		print(f"SHOP INVENTORY")
		print(f"{'='*78}")

		# Separate spell items from regular items
		regular_items = [(n, q) for n, q in shop_data['items'] if not n.startswith('spell_')]
		spell_items = [(n, q) for n, q in shop_data['items'] if n.startswith('spell_')]

		print(f"\nREGULAR ITEMS ({len(regular_items)}):")
		for name, qty in regular_items:
			print(f"  {name} x{qty}")

		if spell_items:
			print(f"\nSPELL SCROLLS/ITEMS ({len(spell_items)}):")
			for name, qty in spell_items:
				print(f"  {name} x{qty}")

		print(f"\nSPELLS ({len(shop_data['spells'])}):")
		for name, qty in shop_data['spells']:
			print(f"  {name} x{qty}")

		print(f"\nUNITS ({len(shop_data['units'])}):")
		for name, qty in shop_data['units']:
			print(f"  {name} x{qty}")

		print(f"\n{'='*78}")
		print(f"TOTALS:")
		print(f"  Regular Items: {len(regular_items)}")
		print(f"  Spell Items: {len(spell_items)}")
		print(f"  Spells: {len(shop_data['spells'])}")
		print(f"  Units: {len(shop_data['units'])}")
		print(f"  Grand Total: {len(regular_items) + len(spell_items) + len(shop_data['spells']) + len(shop_data['units'])}")
