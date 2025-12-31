#!/usr/bin/env python3
"""
Validate shop extractor on both save files
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
	"""Parse slash-separated format: name/qty/name/qty/..."""
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
	"""Parse items section - quantity stored in slruck metadata field"""
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
	"""Parse spells section - quantity stored as first uint32 after name"""
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


def extract_all_shops(data: bytes, save_name: str) -> list:
	"""Extract all shops from save file"""
	print(f"Processing {save_name}...")
	print("Finding all shop IDs...")
	shops = find_all_shop_ids(data)
	print(f"Found {len(shops)} shops\n")

	all_shop_data = []

	for i, (shop_id, shop_pos) in enumerate(shops):
		if (i + 1) % 50 == 0 or i == 0:
			print(f"  [{i+1}/{len(shops)}] Parsing shops...")

		shop_data = parse_shop(data, shop_id, shop_pos)
		all_shop_data.append(shop_data)

	return all_shop_data


def process_save_file(input_file: str, output_file: str, save_name: str) -> dict:
	"""Process a save file and return statistics"""
	print(f"\n{'='*78}")
	print(f"PROCESSING: {save_name}")
	print(f"{'='*78}\n")

	print(f"Input:  {input_file}")
	print(f"Output: {output_file}\n")

	# Load save data
	with open(input_file, 'rb') as f:
		data = f.read()

	print(f"Save file size: {len(data):,} bytes\n")

	# Extract all shops
	shops = extract_all_shops(data, save_name)

	# Statistics
	total_garrison = sum(len(s['garrison']) for s in shops)
	total_items = sum(len(s['items']) for s in shops)
	total_units = sum(len(s['units']) for s in shops)
	total_spells = sum(len(s['spells']) for s in shops)
	total_products = total_garrison + total_items + total_units + total_spells

	# Shops with content
	shops_with_garrison = sum(1 for s in shops if s['garrison'])
	shops_with_items = sum(1 for s in shops if s['items'])
	shops_with_units = sum(1 for s in shops if s['units'])
	shops_with_spells = sum(1 for s in shops if s['spells'])
	shops_with_any = sum(1 for s in shops if s['garrison'] or s['items'] or s['units'] or s['spells'])

	stats = {
		'save_name': save_name,
		'file_size': len(data),
		'total_shops': len(shops),
		'shops_with_content': shops_with_any,
		'shops_with_garrison': shops_with_garrison,
		'shops_with_items': shops_with_items,
		'shops_with_units': shops_with_units,
		'shops_with_spells': shops_with_spells,
		'total_garrison': total_garrison,
		'total_items': total_items,
		'total_units': total_units,
		'total_spells': total_spells,
		'total_products': total_products
	}

	print(f"\n{'='*78}")
	print(f"EXTRACTION COMPLETE: {save_name}")
	print(f"{'='*78}\n")

	print(f"Total shops:           {len(shops)}")
	print(f"Shops with content:    {shops_with_any}")
	print(f"  - With garrison:     {shops_with_garrison}")
	print(f"  - With items:        {shops_with_items}")
	print(f"  - With units:        {shops_with_units}")
	print(f"  - With spells:       {shops_with_spells}")
	print()
	print(f"Total garrison:        {total_garrison}")
	print(f"Total items:           {total_items}")
	print(f"Total units:           {total_units}")
	print(f"Total spells:          {total_spells}")
	print(f"Grand total products:  {total_products}")

	# Convert to JSON-friendly format
	json_data = {}
	for shop in shops:
		json_data[shop['shop_id']] = {
			'garrison': [{'name': n, 'quantity': q} for n, q in shop['garrison']],
			'items': [{'name': n, 'quantity': q} for n, q in shop['items']],
			'units': [{'name': n, 'quantity': q} for n, q in shop['units']],
			'spells': [{'name': n, 'quantity': q} for n, q in shop['spells']]
		}

	# Save to JSON
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(json_data, f, indent=2, ensure_ascii=False)

	print(f"\n[SUCCESS] Saved to: {output_file}")

	return stats


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))

	print("="*78)
	print("VALIDATING SHOP EXTRACTOR ON TWO SAVE FILES")
	print("="*78)

	# Process both saves
	save1_input = os.path.join(script_dir, 'tmp', 'decompressed.bin')
	save1_output = os.path.join(script_dir, 'tmp', 'shops_save1_old.json')

	save2_input = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')
	save2_output = os.path.join(script_dir, 'tmp', 'shops_save2_new.json')

	stats1 = process_save_file(save1_input, save1_output, "Save 1 (Old - Played)")
	stats2 = process_save_file(save2_input, save2_output, "Save 2 (New - Fresh)")

	# Summary comparison
	print(f"\n{'='*78}")
	print("COMPARISON SUMMARY")
	print(f"{'='*78}\n")

	print(f"{'Metric':<30s} {'Save 1 (Old)':<20s} {'Save 2 (New)':<20s}")
	print(f"{'-'*30} {'-'*20} {'-'*20}")
	print(f"{'File size':<30s} {stats1['file_size']:>15,} bytes {stats2['file_size']:>15,} bytes")
	print(f"{'Total shops':<30s} {stats1['total_shops']:>20,} {stats2['total_shops']:>20,}")
	print(f"{'Shops with content':<30s} {stats1['shops_with_content']:>20,} {stats2['shops_with_content']:>20,}")
	print(f"{'Total products':<30s} {stats1['total_products']:>20,} {stats2['total_products']:>20,}")
	print(f"  {'- Garrison':<28s} {stats1['total_garrison']:>20,} {stats2['total_garrison']:>20,}")
	print(f"  {'- Items':<28s} {stats1['total_items']:>20,} {stats2['total_items']:>20,}")
	print(f"  {'- Units':<28s} {stats1['total_units']:>20,} {stats2['total_units']:>20,}")
	print(f"  {'- Spells':<28s} {stats1['total_spells']:>20,} {stats2['total_spells']:>20,}")

	print(f"\n{'='*78}")
	print("VALIDATION COMPLETE")
	print(f"{'='*78}\n")

	print("Output files:")
	print(f"  1. {save1_output}")
	print(f"  2. {save2_output}")
