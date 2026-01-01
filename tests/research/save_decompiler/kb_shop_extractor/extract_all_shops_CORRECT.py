#!/usr/bin/env python3
"""
CORRECT SHOP EXTRACTOR - Final version with proper quantity parsing

Quantity storage by section:
- ITEMS: Stored in slruck metadata field as "slot,quantity" string
- SPELLS: Stored as first uint32 after name
- UNITS: Stored in slash-separated format "unit/qty/unit/qty"
- GARRISON: Stored in slash-separated format "unit/qty/unit/qty"
"""
import struct
import re
import json
import os


METADATA_KEYWORDS = {
	'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
	'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}


def is_valid_id(item_id: str) -> bool:
	"""Validate item/spell/unit ID"""
	if not item_id or item_id in METADATA_KEYWORDS or len(item_id) < 5:
		return False
	return bool(re.match(r'^[a-z][a-z0-9_]*$', item_id))


def find_all_shop_ids(data: bytes) -> list:
	"""Find all shop IDs in save file"""
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


def parse_items_section(data: bytes, section_pos: int, next_pos: int) -> list:
	"""
	Parse items section - quantity stored in slruck metadata field
	Format: [length][name][metadata...slruck[length]["slot,qty"]...]
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

					if is_valid_id(name):
						# Scan forward for slruck field (within next 500 bytes)
						scan_pos = pos + 4 + name_length
						quantity = 1  # Default

						for _ in range(125):  # 125 * 4 = 500 bytes
							if scan_pos + 10 > search_end:
								break

							# Look for "slruck" string
							if data[scan_pos:scan_pos+6] == b'slruck':
								try:
									val_len = struct.unpack('<I', data[scan_pos+6:scan_pos+10])[0]
									if 1 <= val_len <= 20:
										val_str = data[scan_pos+10:scan_pos+10+val_len].decode('ascii', errors='strict')
										# Parse "slot,qty" format
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

	return sorted([(name, qty) for name, qty in items])


def parse_spells_section(data: bytes, section_pos: int, next_pos: int) -> list:
	"""
	Parse spells section - quantity stored as first uint32 after name
	Format: [length][name][quantity][next spell...]
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

					if is_valid_id(name):
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

	return sorted([(name, qty) for name, qty in spells_dict.items()])


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

	# Parse garrison (slash-separated)
	if garrison_pos and items_pos:
		result['garrison'] = parse_slash_separated(data, garrison_pos, items_pos)

	# Parse items (slruck-based quantity)
	if items_pos:
		next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
		result['items'] = parse_items_section(data, items_pos, next_pos)

	# Parse units (slash-separated)
	if units_pos:
		next_pos = spells_pos if spells_pos else shop_pos
		result['units'] = parse_slash_separated(data, units_pos, next_pos)

	# Parse spells (first uint32)
	if spells_pos:
		result['spells'] = parse_spells_section(data, spells_pos, shop_pos)

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
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	print("="*78)
	print("CORRECT SHOP EXTRACTOR")
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
	output_file = os.path.join(script_dir, 'tmp', 'all_shops_CORRECT.json')

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

	print(f"\n[SUCCESS] Saved to: tmp/all_shops_CORRECT.json")

	# Verify test shop
	print(f"\n{'='*78}")
	print("Verifying test shop: itext_m_portland_6820")
	print(f"{'='*78}\n")

	test_shop = next((s for s in shops if s['shop_id'] == 'itext_m_portland_6820'), None)
	if test_shop:
		print(f"Items ({len(test_shop['items'])} total):")
		for name, qty in test_shop['items']:
			print(f"  {name:40s} x{qty}")

		print(f"\nUnits ({len(test_shop['units'])} total):")
		for name, qty in test_shop['units']:
			print(f"  {name:40s} x{qty}")

		print(f"\nSpells ({len(test_shop['spells'])} total):")
		for name, qty in test_shop['spells']:
			print(f"  {name:40s} x{qty}")
