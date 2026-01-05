#!/usr/bin/env python3
"""
Find crystal items with high quantities to understand format
"""
import struct
import re
import os


def find_items_with_high_quantity(data: bytes, section_start: int, section_end: int) -> None:
	"""Find items with quantity > 1000 to identify crystals"""
	pos = section_start

	print(f"Searching from {section_start} to {section_end} ({section_end - section_start} bytes)")
	print()

	found_items = []

	while pos < section_end - 20:
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

					if re.match(r'^[a-z][a-z0-9_]*$', name):
						# Try reading next few uint32 values
						values = []
						for i in range(10):
							offset = pos + 4 + name_length + (i * 4)
							if offset + 4 <= len(data):
								val = struct.unpack('<I', data[offset:offset+4])[0]
								values.append(val)

						# Check if any value is > 1000 (likely a crystal quantity)
						high_vals = [v for v in values if 1000 < v < 100000]

						if high_vals:
							print(f"Item: {name:40s} at {pos}")
							print(f"  Next 10 uint32: {values}")
							print(f"  High values: {high_vals}")

							# Hex dump
							dump_start = pos + 4 + name_length
							print(f"  Hex after name:")
							hex_bytes = data[dump_start:dump_start+40]
							print(f"    {' '.join(f'{b:02x}' for b in hex_bytes)}")
							print()

							found_items.append((name, pos, values))
							pos += 4 + name_length + 4
							continue
				except:
					pass
		except:
			pass

		pos += 1

	return found_items


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Test shop positions for shop that should have crystals
	# Let's try first few shops
	print("="*78)
	print("SEARCHING FOR CRYSTAL ITEMS (quantity > 1000)")
	print("="*78)
	print()

	# Search in shop itext_m_zcom_1422
	shop_pos = 630874
	items_pos = 627891
	spells_pos = 629793

	print("Shop: itext_m_zcom_1422")
	print("Items section:")
	find_items_with_high_quantity(data, items_pos, spells_pos)
