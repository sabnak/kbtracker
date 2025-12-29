#!/usr/bin/env python3
"""
Extract shop inventory mappings from save file
"""
import struct
import re
import json


def find_shop_sections(data: bytes) -> list:
	"""Find all bshop sections in the data"""
	shops = []
	pos = 0

	while True:
		pos = data.find(b'bshop', pos)
		if pos == -1:
			break

		shops.append(pos)
		pos += 1

	return shops


def extract_items_from_section(data: bytes, start_pos: int, max_search: int = 8192) -> list:
	"""Extract items from a .items section"""
	items = []

	# Search for .items marker
	items_pos = data.find(b'.items', start_pos, start_pos + max_search)
	if items_pos == -1:
		return []

	# Parse items until we hit another section marker or run out of data
	pos = items_pos + len(b'.items')
	end_pos = min(len(data), pos + 4096)

	while pos < end_pos:
		# Look for item name pattern (ASCII string without "itm_" prefix)
		# Items appear after certain markers
		try:
			# Check if we hit another section marker
			next_section = data[pos:pos+20]
			if b'.shopunits' in next_section or b'.spells' in next_section or b'bshop' in next_section:
				break

			# Look for length-prefixed ASCII strings that might be item IDs
			if pos + 4 < len(data):
				length = struct.unpack('<I', data[pos:pos+4])[0]

				if 5 <= length <= 100:  # Reasonable item name length
					try:
						item_data = data[pos+4:pos+4+length]
						# Try to decode as ASCII
						item_name = item_data.decode('ascii')

						# Check if it looks like an item ID
						if ('addon' in item_name or 'scroll' in item_name or 'potion' in item_name or
							'armor' in item_name or 'sword' in item_name or 'weapon' in item_name or
							'_' in item_name) and not item_name.startswith('.'):

							items.append(item_name)
							pos += 4 + length
							continue
					except:
						pass

		except:
			pass

		pos += 1

	return items


def extract_shop_id_from_section(data: bytes, shop_pos: int) -> str:
	"""Extract shop ID from a shop section"""
	# Search for itext_m_ pattern in UTF-16 near this position
	search_start = max(0, shop_pos - 2048)
	search_end = min(len(data), shop_pos + 8192)
	chunk = data[search_start:search_end]

	try:
		text_utf16 = chunk.decode('utf-16-le', errors='ignore')

		# Find shop IDs
		pattern = r'itext_m_\w+_\d+'
		matches = re.findall(pattern, text_utf16)

		if matches:
			# Return the first match
			return matches[0]

	except:
		pass

	return None


def extract_all_shop_inventories(data: bytes) -> dict:
	"""Extract all shop to items mappings"""
	print("Searching for shop sections...")
	shop_positions = find_shop_sections(data)
	print(f"Found {len(shop_positions)} shop sections\n")

	shop_inventories = {}
	processed_shops = set()

	for i, shop_pos in enumerate(shop_positions[:50]):  # Process first 50
		# Extract shop ID
		shop_id = extract_shop_id_from_section(data, shop_pos)

		if shop_id and shop_id not in processed_shops:
			# Extract items
			items = extract_items_from_section(data, shop_pos)

			if items:
				shop_inventories[shop_id] = items
				processed_shops.add(shop_id)
				print(f"[{len(shop_inventories)}] {shop_id}: {len(items)} items")
				for item in items[:5]:  # Show first 5
					print(f"  - {item}")
				if len(items) > 5:
					print(f"  ... and {len(items) - 5} more")

	return shop_inventories


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print(f"File size: {len(data):,} bytes\n")

	# Extract shop inventories
	shop_inventories = extract_all_shop_inventories(data)

	print(f"\n{'='*60}")
	print(f"Total shops with inventories: {len(shop_inventories)}")
	print(f"{'='*60}")

	# Save to JSON
	output_file = os.path.join(script_dir, 'tmp', 'shop_inventories.json')
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(shop_inventories, f, indent=2, ensure_ascii=False)

	print(f"\n[+] Saved shop inventories to: tmp/shop_inventories.json")
