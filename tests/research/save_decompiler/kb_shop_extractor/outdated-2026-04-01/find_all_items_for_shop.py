#!/usr/bin/env python3
"""
Find ALL .items sections near a specific shop
"""
import struct
import os


def find_shop_section(data: bytes, shop_id: str) -> int:
	"""Find the position of a specific shop by ID"""
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)
	return pos if pos != -1 else None


def find_all_items_sections_near(data: bytes, shop_pos: int, search_range: int = 16384):
	"""Find ALL .items sections near shop ID"""
	search_start = max(0, shop_pos - search_range)
	search_end = min(len(data), shop_pos + search_range)

	sections = []
	pos = search_start

	while True:
		items_pos = data.find(b'.items', pos, search_end)
		if items_pos == -1:
			break

		sections.append(items_pos)
		pos = items_pos + 1

	return sections


def parse_items_from_section(data: bytes, section_pos: int) -> list:
	"""Parse items from a .items section"""
	items = []
	pos = section_pos + len(b'.items')

	# Skip to 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4

	# Read item count
	if pos + 4 > len(data):
		return []

	item_count = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	# Skip metadata
	pos += 8

	# Parse each item
	for _ in range(min(item_count, 100)):
		if pos + 4 > len(data):
			break

		# Read length
		item_length = struct.unpack('<I', data[pos:pos+4])[0]
		pos += 4

		if item_length <= 0 or item_length > 200:
			break

		if pos + item_length > len(data):
			break

		# Read item name
		try:
			item_name = data[pos:pos+item_length].decode('ascii')
			if item_name and '_' in item_name and not item_name.startswith('.'):
				items.append(item_name)

			pos += item_length

			# Skip metadata and find next item
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

	return items


def show_hex(data: bytes, pos: int, context: int = 64):
	"""Show hex context around position"""
	start = max(0, pos - context)
	chunk = data[start:pos+context]

	result = []
	for i in range(0, len(chunk), 16):
		offset = start + i
		line = chunk[i:i+16]
		hex_part = ' '.join(f'{b:02X}' for b in line).ljust(48)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)

		marker = '>>>' if start + i <= pos < start + i + 16 else '   '
		result.append(f"{marker} {offset:08X}  {hex_part}  {ascii_part}")

	return '\n'.join(result)


def investigate_all_sections(data: bytes, shop_id: str):
	"""Investigate ALL .items sections near a shop"""
	print(f"Investigating all .items sections for shop: {shop_id}")
	print("=" * 78)

	# Find shop
	shop_pos = find_shop_section(data, shop_id)
	if shop_pos is None:
		print(f"Shop {shop_id} not found!")
		return

	print(f"\nShop ID found at offset: {shop_pos} (0x{shop_pos:X})")

	# Find all .items sections
	sections = find_all_items_sections_near(data, shop_pos)
	print(f"\nFound {len(sections)} .items sections within 16KB range:")

	for i, section_pos in enumerate(sections):
		distance = section_pos - shop_pos
		print(f"\n{'='*78}")
		print(f"Section {i+1}: Offset {section_pos} (0x{section_pos:X})")
		print(f"Distance from shop: {distance:+d} bytes")

		# Parse items
		items = parse_items_from_section(data, section_pos)

		print(f"Items found: {len(items)}")
		for item in items:
			print(f"  - {item}")

		# Show context
		print(f"\nContext around .items marker:")
		print(show_hex(data, section_pos, 48))


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Investigate the problematic shop
	investigate_all_sections(data, 'itext_m_zcom_1422')

	print("\n" + "=" * 78)
	print("Now let's check what tournament_helm looks like...")
	print("=" * 78)

	# Search for tournament_helm in the data
	search_term = b'tournament_helm'
	pos = 0
	found_count = 0

	while True:
		pos = data.find(search_term, pos)
		if pos == -1:
			break

		found_count += 1
		print(f"\n[{found_count}] Found 'tournament_helm' at offset {pos} (0x{pos:X})")

		# Check if there's a length prefix before it
		if pos >= 4:
			possible_length = struct.unpack('<I', data[pos-4:pos])[0]
			print(f"    Possible length prefix: {possible_length}")
			if possible_length == len(search_term):
				print(f"    ✓ This looks like a length-prefixed string!")

		# Show context
		print(show_hex(data, pos, 32))

		pos += 1

	if found_count == 0:
		print("\nNo occurrences of 'tournament_helm' found in save file!")
