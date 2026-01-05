#!/usr/bin/env python3
"""
Parse complete shop data: items, spells, and units with quantities
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


def find_sections_near(data: bytes, marker: bytes, shop_pos: int, search_range: int = 16384) -> list:
	"""Find all sections with given marker near shop"""
	search_start = max(0, shop_pos - search_range)
	search_end = min(len(data), shop_pos + search_range)

	sections = []
	pos = search_start

	while True:
		section_pos = data.find(marker, pos, search_end)
		if section_pos == -1:
			break
		sections.append(section_pos)
		pos = section_pos + 1

	return sections


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


def parse_shop_complete(data: bytes, shop_id: str) -> dict:
	"""
	Parse complete shop data: items, spells, units

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

	# Find and parse .items sections
	items_sections = find_sections_near(data, b'.items', shop_pos)
	print(f"\nFound {len(items_sections)} .items sections near {shop_id}")
	for section_pos in items_sections:
		items = parse_section_with_quantities(data, section_pos, len(b'.items'))
		if items:
			distance = section_pos - shop_pos
			print(f"  Section at {distance:+d} bytes: {len(items)} items")
			for name, qty in items:
				print(f"    {name} x{qty}")
			result['items'].extend(items)

	# Find and parse .spells sections
	spells_sections = find_sections_near(data, b'.spells', shop_pos)
	print(f"\nFound {len(spells_sections)} .spells sections near {shop_id}")
	for section_pos in spells_sections:
		spells = parse_section_with_quantities(data, section_pos, len(b'.spells'))
		if spells:
			distance = section_pos - shop_pos
			print(f"  Section at {distance:+d} bytes: {len(spells)} spells")
			for name, qty in spells:
				print(f"    {name} x{qty}")
			result['spells'].extend(spells)

	# Find and parse .shopunits sections
	units_sections = find_sections_near(data, b'.shopunits', shop_pos)
	print(f"\nFound {len(units_sections)} .shopunits sections near {shop_id}")
	for section_pos in units_sections:
		units = parse_section_with_quantities(data, section_pos, len(b'.shopunits'))
		if units:
			distance = section_pos - shop_pos
			print(f"  Section at {distance:+d} bytes: {len(units)} units")
			for name, qty in units:
				print(f"    {name} x{qty}")
			result['units'].extend(units)

	# Remove duplicates (keep highest quantity)
	for key in result:
		items_dict = {}
		for name, qty in result[key]:
			if name not in items_dict or items_dict[name] < qty:
				items_dict[name] = qty
		result[key] = [(name, qty) for name, qty in sorted(items_dict.items())]

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
	print(f"Parsing complete shop data for: {shop_id}")
	print(f"{'='*78}")

	shop_data = parse_shop_complete(data, shop_id)

	if shop_data:
		print(f"\n{'='*78}")
		print(f"COMPLETE SHOP INVENTORY")
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
