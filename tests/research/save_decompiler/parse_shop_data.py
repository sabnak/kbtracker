#!/usr/bin/env python3
"""
Parse shop data from decompressed save file
"""
import struct
import re


def find_all_strings(data: bytes) -> list:
	"""Find all UTF-16 LE strings with 'strg' marker"""
	strings = []
	i = 0

	while i < len(data) - 8:
		# Look for 'strg' marker
		if data[i:i+4] == b'strg':
			try:
				# Read length (in bytes)
				length = struct.unpack('<I', data[i+4:i+8])[0]

				# Reasonable length check (1-500 characters = 2-1000 bytes in UTF-16)
				if 2 <= length <= 1000 and length % 2 == 0:
					# Read UTF-16 LE string
					string_data = data[i+8:i+8+length]
					text = string_data.decode('utf-16-le', errors='ignore')

					# Check if it's a valid string (printable chars)
					if text and all(c.isprintable() or c == '\x00' for c in text):
						strings.append({
							'offset': i,
							'length': length,
							'text': text.rstrip('\x00')
						})

					i += 8 + length
					continue
			except:
				pass

		i += 1

	return strings


def filter_shop_ids(strings: list) -> list:
	"""Filter for shop-related strings"""
	shop_strings = []

	for s in strings:
		text = s['text']
		# Look for itext_m_ pattern (shop identifiers)
		if text.startswith('itext_m_'):
			shop_strings.append(s)

	return shop_strings


def find_items_near_shop(data: bytes, shop_offset: int) -> list:
	"""Search for item IDs near a shop definition"""
	# Search 4KB before and after the shop ID
	start = max(0, shop_offset - 4096)
	end = min(len(data), shop_offset + 4096)
	chunk = data[start:end]

	# Find all 'strg' strings in this chunk
	items = []
	i = 0
	while i < len(chunk) - 8:
		if chunk[i:i+4] == b'strg':
			try:
				length = struct.unpack('<I', chunk[i+4:i+8])[0]
				if 2 <= length <= 1000 and length % 2 == 0:
					string_data = chunk[i+8:i+8+length]
					text = string_data.decode('utf-16-le', errors='ignore').rstrip('\x00')

					# Check if it looks like an item ID
					if text.startswith('itm_') or text.startswith('spell_'):
						items.append({
							'offset': start + i,
							'text': text
						})

					i += 8 + length
					continue
			except:
				pass
		i += 1

	return items


def analyze_shop_structure(data: bytes, shop_strings: list):
	"""Analyze the structure around shop definitions"""
	print("=== Shop Data Analysis ===\n")

	shops_with_items = {}

	for shop in shop_strings[:10]:  # Analyze first 10 shops
		shop_id = shop['text']
		print(f"Shop: {shop_id} (offset: 0x{shop['offset']:08x})")

		# Find items near this shop
		items = find_items_near_shop(data, shop['offset'])

		if items:
			print(f"  Found {len(items)} nearby item/spell IDs:")
			for item in items[:10]:  # Show first 10
				print(f"    - {item['text']}")

			# Store for later
			if shop_id not in shops_with_items:
				shops_with_items[shop_id] = []
			shops_with_items[shop_id].extend([i['text'] for i in items])
		else:
			print(f"  No items found nearby")

		print()

	return shops_with_items


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print(f"File size: {len(data):,} bytes\n")

	# Find all UTF-16 strings
	print("Extracting all strings...")
	all_strings = find_all_strings(data)
	print(f"Found {len(all_strings)} total strings\n")

	# Filter for shop IDs
	shop_strings = filter_shop_ids(all_strings)
	print(f"Found {len(shop_strings)} shop-related strings\n")

	# Show first 20 shop IDs
	print("First 20 shop IDs:")
	for s in shop_strings[:20]:
		print(f"  - {s['text']}")
	print()

	# Analyze shop structure
	shops_with_items = analyze_shop_structure(data, shop_strings)

	# Save results
	with open(os.path.join(script_dir, 'tmp', 'shop_ids_utf16.txt'), 'w', encoding='utf-8') as f:
		for s in shop_strings:
			f.write(f"{s['text']}\n")

	print(f"\n[+] Saved {len(shop_strings)} shop IDs to: tmp/shop_ids_utf16.txt")
