#!/usr/bin/env python3
"""
Examine the exact structure around a shop ID to understand section grouping
"""
import struct
import os


def hex_dump(data: bytes, start: int, length: int = 512):
	"""Print hex dump"""
	for i in range(0, length, 16):
		offset = start + i
		if offset >= len(data):
			break

		chunk = data[offset:offset+16]
		hex_part = ' '.join(f'{b:02X}' for b in chunk).ljust(48)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
		print(f"{offset:08X}  {hex_part}  {ascii_part}")


def find_shop_section(data: bytes, shop_id: str) -> int:
	"""Find shop position by ID"""
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)
	return pos if pos != -1 else None


def find_markers_around(data: bytes, center: int, search_range: int = 20000):
	"""Find all section markers around a position"""
	search_start = max(0, center - search_range)
	search_end = min(len(data), center + search_range)

	markers = {
		b'.items': [],
		b'.spells': [],
		b'.shopunits': [],
		b'.shop': [],
		b'.temp': []
	}

	for marker in markers:
		pos = search_start
		while True:
			found_pos = data.find(marker, pos, search_end)
			if found_pos == -1:
				break
			markers[marker].append(found_pos - center)
			pos = found_pos + 1

	return markers


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	shop_id = 'itext_m_zcom_1422'
	shop_pos = find_shop_section(data, shop_id)

	print(f"Shop: {shop_id}")
	print(f"Position: {shop_pos} (0x{shop_pos:X})")
	print(f"\n{'='*78}")
	print("Markers within ±20KB:")
	print(f"{'='*78}\n")

	markers = find_markers_around(data, shop_pos)

	for marker_name, positions in sorted(markers.items()):
		marker_str = marker_name.decode('ascii')
		if positions:
			print(f"{marker_str}:")
			for pos in sorted(positions):
				print(f"  {pos:+6d} bytes (offset {shop_pos + pos})")
			print()

	# Show hex dump around shop ID
	print(f"\n{'='*78}")
	print("Hex dump around shop ID (-256 to +256 bytes):")
	print(f"{'='*78}\n")
	hex_dump(data, shop_pos - 256, 512)

	# Check what comes immediately before shop ID
	print(f"\n{'='*78}")
	print("Looking backward from shop ID for section markers...")
	print(f"{'='*78}\n")

	for search_dist in [500, 1000, 2000, 3000, 5000, 10000]:
		search_start = shop_pos - search_dist
		chunk = data[search_start:shop_pos]

		# Find last occurrence of each marker
		for marker in [b'.shopunits', b'.spells', b'.items']:
			last_pos = chunk.rfind(marker)
			if last_pos != -1:
				actual_pos = search_start + last_pos
				distance = shop_pos - actual_pos
				print(f"{marker.decode('ascii'):12s} within -{search_dist:5d}: found at -{distance:5d} bytes (offset {actual_pos})")
