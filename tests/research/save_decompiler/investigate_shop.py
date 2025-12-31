#!/usr/bin/env python3
"""
Investigate specific shop structure to understand metadata vs actual items
"""
import struct
import os


def find_shop_section(data: bytes, shop_id: str) -> int:
	"""Find the position of a specific shop by ID"""
	# Encode shop ID as UTF-16 LE
	shop_bytes = shop_id.encode('utf-16-le')

	pos = data.find(shop_bytes)
	return pos if pos != -1 else None


def hex_dump(data: bytes, start: int, length: int = 512):
	"""Print hex dump with ASCII preview"""
	print(f"\nHex dump starting at offset {start} (0x{start:X}):")
	print("=" * 78)

	for i in range(0, length, 16):
		offset = start + i
		if offset >= len(data):
			break

		chunk = data[offset:offset+16]

		# Hex part
		hex_part = ' '.join(f'{b:02X}' for b in chunk)
		hex_part = hex_part.ljust(48)

		# ASCII part
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)

		print(f"{offset:08X}  {hex_part}  {ascii_part}")


def find_items_section_near(data: bytes, shop_pos: int, search_range: int = 16384):
	"""Find .items section near shop ID"""
	search_start = max(0, shop_pos - search_range)
	search_end = min(len(data), shop_pos + search_range)

	# Search forward
	items_pos = data.find(b'.items', search_start, search_end)
	return items_pos


def parse_item_detailed(data: bytes, pos: int) -> tuple:
	"""Parse a single item with detailed metadata inspection"""
	if pos + 4 > len(data):
		return None, pos

	# Read length
	item_length = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	if item_length <= 0 or item_length > 200 or pos + item_length > len(data):
		return None, pos

	# Read item name
	try:
		item_name = data[pos:pos+item_length].decode('ascii', errors='strict')
		item_end = pos + item_length

		# Read some metadata after the item
		metadata_sample = data[item_end:item_end+100]

		result = {
			'name': item_name,
			'length': item_length,
			'start_offset': pos - 4,
			'end_offset': item_end,
			'metadata_sample': metadata_sample[:50]
		}

		return result, item_end

	except:
		return None, pos + item_length


def investigate_shop(data: bytes, shop_id: str):
	"""Investigate a specific shop's data structure"""
	print(f"Investigating shop: {shop_id}")
	print("=" * 78)

	# Find shop
	shop_pos = find_shop_section(data, shop_id)
	if shop_pos is None:
		print(f"Shop {shop_id} not found!")
		return

	print(f"\nShop ID found at offset: {shop_pos} (0x{shop_pos:X})")

	# Find .items section
	items_pos = find_items_section_near(data, shop_pos)
	if items_pos is None:
		print("No .items section found near shop!")
		return

	print(f".items section found at offset: {items_pos} (0x{items_pos:X})")
	print(f"Distance: {abs(items_pos - shop_pos)} bytes")

	# Show hex dump around .items section
	hex_dump(data, items_pos - 32, 256)

	# Parse items in detail
	print("\n" + "=" * 78)
	print("Parsing items in detail:")
	print("=" * 78)

	pos = items_pos + len(b'.items')

	# Skip to 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		print("No 'strg' marker found!")
		return

	print(f"\n'strg' marker at offset: {strg_pos} (0x{strg_pos:X})")
	pos = strg_pos + 4

	# Read item count
	item_count = struct.unpack('<I', data[pos:pos+4])[0]
	print(f"Item count: {item_count}")
	pos += 4

	# Skip metadata
	pos += 8

	# Parse each item
	for i in range(min(item_count, 20)):
		item_info, new_pos = parse_item_detailed(data, pos)

		if item_info is None:
			print(f"\n[{i}] Failed to parse item at offset {pos}")
			break

		print(f"\n[{i}] Item: {item_info['name']}")
		print(f"    Offset: {item_info['start_offset']} - {item_info['end_offset']}")
		print(f"    Length: {item_info['length']}")

		# Show hex dump of item name bytes
		item_bytes = data[item_info['start_offset']:item_info['end_offset']+20]
		print(f"    Hex: {' '.join(f'{b:02X}' for b in item_bytes[:40])}")

		# Show metadata sample
		meta_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in item_info['metadata_sample'])
		print(f"    Metadata preview: {meta_ascii}")

		# Try to find next item
		# Look for next length marker
		max_skip = 200
		found_next = False
		for skip in range(max_skip):
			if new_pos + skip + 4 > len(data):
				break

			next_len = struct.unpack('<I', data[new_pos+skip:new_pos+skip+4])[0]
			if 5 <= next_len <= 100:
				try:
					test_name = data[new_pos+skip+4:new_pos+skip+4+min(next_len, 50)].decode('ascii', errors='strict')
					if '_' in test_name and test_name[0].isalpha():
						pos = new_pos + skip
						found_next = True
						print(f"    Next item at +{skip} bytes")
						break
				except:
					pass

		if not found_next:
			print(f"    No more items found (searched {max_skip} bytes)")
			break


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Investigate the problematic shop
	investigate_shop(data, 'itext_m_zcom_1422')
