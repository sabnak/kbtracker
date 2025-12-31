#!/usr/bin/env python3
"""
FIXED COMPLETE SHOP EXTRACTOR

Fixes:
1. Items/Spells have quantity = 1 (not stored in save file)
2. Filter out metadata keywords (count, flags, lvars, etc.)
3. Garrison/Units keep actual quantities from slash-separated format
"""
import struct
import re
import json
import os


# Known metadata keywords to filter out
METADATA_KEYWORDS = {
	'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
	'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}


def is_valid_id(item_id: str) -> bool:
	"""Validate item/spell/unit ID"""
	if not item_id:
		return False

	# Filter out metadata keywords
	if item_id in METADATA_KEYWORDS:
		return False

	# Must match pattern
	pattern = r'^[a-z][a-z0-9_]*$'
	if not re.match(pattern, item_id):
		return False

	# Minimum length (real items are usually longer)
	if len(item_id) < 5:
		return False

	return True


def find_all_shop_ids(data: bytes) -> list:
	"""Find all shop IDs in save file"""
	shops = []
	pattern = rb'itext_m_\w+_\d+'

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


def find_preceding_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 5000) -> int:
	"""Find section marker immediately BEFORE shop ID"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos
	return None


def parse_slash_separated(data: bytes, section_pos: int, next_pos: int) -> list:
	"""
	Parse slash-separated format: name/qty/name/qty/...
	Used by: .garrison and .shopunits
	Returns items WITH quantities from the file
	"""
	pos = section_pos

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, next_pos)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4

	# Read string length
	if pos + 4 > len(data):
		return []

	str_length = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	if str_length <= 0 or str_length > 5000:
		return []

	if pos + str_length > len(data):
		return []

	# Read and parse string
	try:
		content_str = data[pos:pos+str_length].decode('ascii')
		parts = content_str.split('/')

		items = []
		i = 0
		while i < len(parts) - 1:
			name = parts[i]
			try:
				quantity = int(parts[i + 1])
				if is_valid_id(name):
					items.append((name, quantity))
				i += 2
			except:
				i += 1

		return items

	except:
		return []


def parse_entry_based(data: bytes, section_pos: int, next_pos: int) -> list:
	"""
	Parse entry-based format: length/name/metadata/...
	Used by: .items and .spells

	IMPORTANT: Items/Spells DON'T have shop quantities in save file!
	All items/spells have quantity = 1
	"""
	items_set = set()
	pos = section_pos
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

					if is_valid_id(name):
						items_set.add(name)
						pos += 4 + name_length + 4
						continue

				except:
					pass

		except:
			pass

		pos += 1

	# Return with quantity = 1 for all items
	return sorted([(name, 1) for name in items_set])


def parse_shop(data: bytes, shop_id: str, shop_pos: int) -> dict:
	"""Parse complete shop with all 4 sections"""
	result = {
		'shop_id': shop_id,
		'garrison': [],
		'items': [],
		'units': [],
		'spells': []
	}

	# Find preceding sections
	garrison_pos = find_preceding_section(data, b'.garrison', shop_pos, 5000)
	items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
	units_pos = find_preceding_section(data, b'.shopunits', shop_pos, 5000)
	spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)

	# Parse garrison (slash-separated, WITH quantities)
	if garrison_pos and items_pos:
		result['garrison'] = parse_slash_separated(data, garrison_pos, items_pos)

	# Parse items (entry-based, quantity = 1)
	if items_pos:
		next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
		result['items'] = parse_entry_based(data, items_pos, next_pos)

	# Parse units (slash-separated, WITH quantities)
	if units_pos:
		next_pos = spells_pos if spells_pos else shop_pos
		result['units'] = parse_slash_separated(data, units_pos, next_pos)

	# Parse spells (entry-based, quantity = 1)
	if spells_pos:
		result['spells'] = parse_entry_based(data, spells_pos, shop_pos)

	return result


def extract_all_shops(data: bytes) -> list:
	"""Extract all shops from save file"""
	print("Finding all shop IDs...")
	shops = find_all_shop_ids(data)
	print(f"Found {len(shops)} shops\n")

	all_shop_data = []

	for i, (shop_id, shop_pos) in enumerate(shops):
		print(f"[{i+1}/{len(shops)}] Parsing {shop_id}...")

		shop_data = parse_shop(data, shop_id, shop_pos)

		# Count items
		total = (len(shop_data['garrison']) + len(shop_data['items']) +
		         len(shop_data['units']) + len(shop_data['spells']))

		print(f"  Garrison: {len(shop_data['garrison']):2d}  Items: {len(shop_data['items']):2d}  "
		      f"Units: {len(shop_data['units']):2d}  Spells: {len(shop_data['spells']):2d}  "
		      f"Total: {total:3d}")

		all_shop_data.append(shop_data)

	return all_shop_data


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("="*78)
	print("FIXED COMPLETE SHOP EXTRACTOR")
	print("="*78)
	print()

	print("Loading save data...")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print(f"Save file size: {len(data):,} bytes\n")

	# Extract all shops
	shops = extract_all_shops(data)

	print(f"\n{'='*78}")
	print(f"EXTRACTION COMPLETE")
	print(f"{'='*78}\n")

	# Statistics
	total_garrison = sum(len(s['garrison']) for s in shops)
	total_items = sum(len(s['items']) for s in shops)
	total_units = sum(len(s['units']) for s in shops)
	total_spells = sum(len(s['spells']) for s in shops)

	print(f"Total shops:     {len(shops)}")
	print(f"Total garrison:  {total_garrison}")
	print(f"Total items:     {total_items}")
	print(f"Total units:     {total_units}")
	print(f"Total spells:    {total_spells}")
	print(f"Grand total:     {total_garrison + total_items + total_units + total_spells}")

	# Save to JSON
	output_file = os.path.join(script_dir, 'tmp', 'all_shops_FIXED.json')

	# Convert to JSON-friendly format
	json_data = {}
	for shop in shops:
		json_data[shop['shop_id']] = {
			'garrison': [{'name': n, 'quantity': q} for n, q in shop['garrison']],
			'items': [{'name': n, 'quantity': q} for n, q in shop['items']],
			'units': [{'name': n, 'quantity': q} for n, q in shop['units']],
			'spells': [{'name': n, 'quantity': q} for n, q in shop['spells']]
		}

	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(json_data, f, indent=2, ensure_ascii=False)

	print(f"\n[SUCCESS] Saved to: tmp/all_shops_FIXED.json")

	# Verify test shop
	print(f"\n{'='*78}")
	print("Verifying test shop: itext_m_zcom_1422")
	print(f"{'='*78}\n")

	test_shop = next((s for s in shops if s['shop_id'] == 'itext_m_zcom_1422'), None)
	if test_shop:
		print(f"Items ({len(test_shop['items'])} total):")
		for name, qty in test_shop['items'][:10]:
			print(f"  {name:30s} x{qty}")
		if len(test_shop['items']) > 10:
			print(f"  ... and {len(test_shop['items']) - 10} more")
