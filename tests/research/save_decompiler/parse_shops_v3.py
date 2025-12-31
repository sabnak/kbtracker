#!/usr/bin/env python3
"""
Parse shop inventories from save file - V3 with fixes

Fixes:
1. Off-by-one error: Parse beyond item_count to catch all items
2. Invalid IDs: Validate item IDs against proper pattern
3. Metadata filtering: Reject upgrade/use/item_count/map strings
"""
import struct
import re
import json


def is_valid_item_id(item_id: str) -> bool:
	"""
	Validate if string is a valid game item ID

	Valid pattern: ^[a-z][a-z0-9_]*$
	- Must start with lowercase letter
	- Can contain: lowercase letters, digits, underscores
	- Cannot contain: /, ,, uppercase letters

	Invalid patterns:
	- upgrade/item1,item2/rndid/123
	- use/1/item_add/scroll/scroll/spell/rndid/123
	- item_count/500/victory/40/rndid/123
	- count1/0/count2/0/moral_base/75/rndid/123
	- map/0/image/picture/rndid/123
	"""
	if not item_id:
		return False

	# Must match: lowercase letter followed by lowercase/digits/underscores
	pattern = r'^[a-z][a-z0-9_]*$'
	return bool(re.match(pattern, item_id))


def find_all_items_sections(data: bytes) -> list:
	"""Find all .items sections"""
	sections = []
	pos = 0

	while True:
		pos = data.find(b'.items', pos)
		if pos == -1:
			break
		sections.append(pos)
		pos += 1

	return sections


def parse_items_section(data: bytes, section_pos: int) -> list:
	"""
	Parse items from a .items section

	Improvements:
	- Parse beyond item_count to catch all items
	- Validate each item ID
	- Skip empty/marker items
	"""
	items = []
	pos = section_pos + len(b'.items')

	# Skip to 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4  # Skip 'strg'

	# Read item count (next 4 bytes after strg)
	if pos + 4 > len(data):
		return []

	item_count = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	# Skip some metadata (usually 8 bytes)
	pos += 8

	# Parse items - go beyond count by a few items to catch missing ones
	# This fixes the off-by-one error where last item is missed
	max_items = min(item_count + 10, 150)  # Safety limit + buffer

	items_found = 0

	for i in range(max_items):
		if pos + 4 > len(data):
			break

		# Read length
		item_length = struct.unpack('<I', data[pos:pos+4])[0]
		pos += 4

		# Sanity check - if length is way off, we've probably hit the end
		if item_length <= 0 or item_length > 200:
			break

		if pos + item_length > len(data):
			break

		# Read item name
		try:
			item_name = data[pos:pos+item_length].decode('ascii', errors='strict')

			# Validate item ID
			if is_valid_item_id(item_name):
				items.append(item_name)
				items_found += 1
			# else: Skip invalid items (metadata, upgrade strings, etc.)

			pos += item_length

			# Skip item metadata until next item or end of section
			# Look for next length marker or end of items
			max_skip = 200
			found_next = False
			for skip in range(max_skip):
				if pos + skip + 4 > len(data):
					break

				next_len = struct.unpack('<I', data[pos+skip:pos+skip+4])[0]
				# Check if this looks like a valid item name length
				if 5 <= next_len <= 100:
					# Check if we can decode it as ASCII
					try:
						test_name = data[pos+skip+4:pos+skip+4+min(next_len, 50)].decode('ascii', errors='strict')
						# Check if it looks like an item name (has underscore, starts with letter)
						if '_' in test_name and test_name[0].isalpha():
							pos += skip
							found_next = True
							break
					except:
						pass

			if not found_next:
				# Reached end of items
				break

		except:
			break

	return items


def find_nearest_shop_id(data: bytes, items_pos: int) -> str:
	"""Find the nearest shop ID to an .items section"""
	# Search backwards and forwards for shop ID in UTF-16
	search_range = 16384
	search_start = max(0, items_pos - search_range)
	search_end = min(len(data), items_pos + search_range)

	chunk = data[search_start:search_end]

	try:
		# Decode as UTF-16 and search for shop IDs
		text = chunk.decode('utf-16-le', errors='ignore')

		# Find all shop IDs in this range
		pattern = r'itext_m_\w+_\d+'
		matches = re.findall(pattern, text)

		if matches:
			# Find the closest one to our position
			best_match = None
			best_distance = float('inf')

			for match in matches:
				# Find position of this match in UTF-16
				match_pos_utf16 = text.find(match)
				if match_pos_utf16 != -1:
					# Convert to byte offset (approximate)
					match_byte_offset = search_start + match_pos_utf16 * 2
					distance = abs(match_byte_offset - items_pos)

					if distance < best_distance:
						best_distance = distance
						best_match = match

			return best_match

	except:
		pass

	return None


def extract_all_shop_inventories(data: bytes) -> dict:
	"""Extract shop to items mapping"""
	print("Finding all .items sections...")
	items_sections = find_all_items_sections(data)
	print(f"Found {len(items_sections)} .items sections\n")

	shop_inventories = {}
	total_invalid_filtered = 0

	for i, items_pos in enumerate(items_sections):
		# Parse items
		items = parse_items_section(data, items_pos)

		if not items:
			continue

		# Find associated shop
		shop_id = find_nearest_shop_id(data, items_pos)

		if shop_id:
			# Merge items if shop already exists
			if shop_id not in shop_inventories:
				shop_inventories[shop_id] = []

			# Count new items
			new_items = [item for item in items if item not in shop_inventories[shop_id]]

			shop_inventories[shop_id].extend(new_items)

			if new_items:
				print(f"[{len(shop_inventories)}] {shop_id}: +{len(new_items)} items")
				for item in new_items:
					print(f"  - {item}")

	# Remove duplicates
	for shop_id in shop_inventories:
		shop_inventories[shop_id] = sorted(list(set(shop_inventories[shop_id])))

	return shop_inventories


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Extract inventories
	inventories = extract_all_shop_inventories(data)

	print(f"\n{'='*70}")
	print(f"Extracted {len(inventories)} shops with items")
	print(f"{'='*70}\n")

	# Calculate statistics
	total_items = sum(len(items) for items in inventories.values())
	unique_items = len(set(item for items in inventories.values() for item in items))

	print(f"Total item entries: {total_items}")
	print(f"Unique items: {unique_items}")

	# Show summary of first few shops
	print(f"\nFirst 10 shops:")
	for shop_id, items in sorted(inventories.items())[:10]:
		print(f"  {shop_id}: {len(items)} items")

	# Save to JSON
	output_file = os.path.join(script_dir, 'tmp', 'shop_inventories_v3.json')
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(inventories, f, indent=2, ensure_ascii=False)

	print(f"\n[+] Saved to: tmp/shop_inventories_v3.json")

	# Check specific shop
	test_shop = 'itext_m_zcom_1422'
	if test_shop in inventories:
		print(f"\n{'='*70}")
		print(f"Test: Shop {test_shop}")
		print(f"{'='*70}")
		print(f"Items ({len(inventories[test_shop])}):")
		for item in inventories[test_shop]:
			marker = " [FOUND!]" if item == "tournament_helm" else ""
			print(f"  - {item}{marker}")

		# Check for invalid entries
		if any('/' in item for item in inventories[test_shop]):
			print("\n⚠️ WARNING: Still has invalid entries with '/'")
		else:
			print("\n✓ No invalid entries found")

		if 'tournament_helm' in inventories[test_shop]:
			print("✓ tournament_helm is present!")
		else:
			print("✗ tournament_helm is MISSING!")
