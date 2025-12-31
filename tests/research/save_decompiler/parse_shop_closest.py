#!/usr/bin/env python3
"""
Parse shop data using CLOSEST sections only
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


def find_closest_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 8192) -> int:
	"""Find the closest section with given marker to shop position"""
	search_start = max(0, shop_pos - max_distance)
	search_end = min(len(data), shop_pos + max_distance)

	closest_pos = None
	closest_distance = float('inf')

	pos = search_start
	while True:
		section_pos = data.find(marker, pos, search_end)
		if section_pos == -1:
			break

		distance = abs(section_pos - shop_pos)
		if distance < closest_distance:
			closest_distance = distance
			closest_pos = section_pos

		pos = section_pos + 1

	return closest_pos


def parse_section_with_quantities(data: bytes, section_pos: int, marker_len: int) -> list:
	"""
	Parse section that contains items/spells/units with quantities

	Returns list of tuples: [(name, quantity), ...]
	"""
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

	# Parse items with quantities
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

			# Read quantity (4 bytes after name)
			if pos + 4 <= len(data):
				quantity = struct.unpack('<I', data[pos:pos+4])[0]
			else:
				quantity = 1

			# Validate and add
			if is_valid_id(name) and quantity > 0 and quantity < 10000:
				results.append((name, quantity))

			# Find next item
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


def parse_shop_closest(data: bytes, shop_id: str) -> dict:
	"""
	Parse shop data using CLOSEST section for each type

	Returns: {
		'items': [(name, qty), ...],
		'spells': [(name, qty), ...],
		'units': [(name, qty), ...]
	}
	"""
	shop_pos = find_shop_section(data, shop_id)
	if shop_pos is None:
		return None

	result = {
		'items': [],
		'spells': [],
		'units': []
	}

	print(f"\nShop at offset: {shop_pos} (0x{shop_pos:X})")

	# Find and parse CLOSEST .items section
	items_pos = find_closest_section(data, b'.items', shop_pos)
	if items_pos:
		distance = items_pos - shop_pos
		print(f"Closest .items at {distance:+d} bytes")
		items = parse_section_with_quantities(data, items_pos, len(b'.items'))
		result['items'] = items
		print(f"  Found {len(items)} items")

	# Find and parse CLOSEST .spells section
	spells_pos = find_closest_section(data, b'.spells', shop_pos)
	if spells_pos:
		distance = spells_pos - shop_pos
		print(f"Closest .spells at {distance:+d} bytes")
		spells = parse_section_with_quantities(data, spells_pos, len(b'.spells'))
		result['spells'] = spells
		print(f"  Found {len(spells)} spells")

	# Find and parse CLOSEST .shopunits section
	units_pos = find_closest_section(data, b'.shopunits', shop_pos)
	if units_pos:
		distance = units_pos - shop_pos
		print(f"Closest .shopunits at {distance:+d} bytes")
		units = parse_section_with_quantities(data, units_pos, len(b'.shopunits'))
		result['units'] = units
		print(f"  Found {len(units)} units")

	return result


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Test with the specific shop
	shop_id = 'itext_m_zcom_1422'
	print(f"{'='*78}")
	print(f"Parsing shop (CLOSEST sections): {shop_id}")
	print(f"{'='*78}")

	shop_data = parse_shop_closest(data, shop_id)

	if shop_data:
		print(f"\n{'='*78}")
		print(f"SHOP INVENTORY (using closest sections)")
		print(f"{'='*78}")

		print(f"\nITEMS ({len(shop_data['items'])}):")
		for name, qty in shop_data['items']:
			print(f"  {name} x{qty}")

		print(f"\nSPELLS ({len(shop_data['spells'])}):")
		for name, qty in shop_data['spells']:
			print(f"  {name} x{qty}")

		print(f"\nUNITS ({len(shop_data['units'])}):")
		for name, qty in shop_data['units']:
			print(f"  {name} x{qty}")

		print(f"\n{'='*78}")
		print(f"TOTALS:")
		print(f"  Items: {len(shop_data['items'])}")
		print(f"  Spells: {len(shop_data['spells'])}")
		print(f"  Units: {len(shop_data['units'])}")
		print(f"  Grand Total: {sum(len(v) for v in shop_data.values())}")
