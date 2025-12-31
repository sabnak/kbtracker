#!/usr/bin/env python3
"""
Search ALL items in portland_6820 shop for high quantities
"""
import struct
import os
import re


def find_shop_position(data: bytes, shop_id: str) -> int:
	"""Find shop ID position in binary"""
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)
	return pos


def find_preceding_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 5000) -> int:
	"""Find section marker immediately BEFORE shop ID"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos
	return None


def scan_for_high_values(data: bytes, start: int, end: int) -> None:
	"""Scan for ANY uint32 values > 10000 in the range"""
	print(f"\nScanning from {start} to {end} for values > 10,000...")
	print()

	pos = start
	found = []

	while pos < end - 4:
		val = struct.unpack('<I', data[pos:pos+4])[0]

		if 10000 <= val <= 50000:
			# Found a candidate! Look backwards for name
			print(f"Found value {val:,} at offset {pos}")

			# Try to find if this is preceded by a string
			for back in range(4, 200, 4):
				test_pos = pos - back
				if test_pos < start:
					break

				try:
					# Try reading as name length
					name_len = struct.unpack('<I', data[test_pos-4:test_pos])[0]
					if 5 <= name_len <= 100 and name_len == back - 4:
						try:
							name = data[test_pos:test_pos+name_len].decode('ascii', errors='strict')
							if re.match(r'^[a-z][a-z0-9_]*$', name):
								print(f"  Preceded by name: '{name}' (length {name_len})")
								print(f"  Name starts at: {test_pos}")
								print(f"  Length field at: {test_pos - 4}")

								# Show structure
								print(f"  Structure: [length={name_len}][name={name}][value={val}]")
								print()
								found.append((name, val, pos))
								break
						except:
							pass
				except:
					pass

			if not found or found[-1][2] != pos:
				# No name found
				print(f"  Context (32 bytes before):")
				context = data[max(start, pos-32):pos+4]
				hex_str = ' '.join(f'{b:02x}' for b in context)
				print(f"    {hex_str}")
				ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
				print(f"    {ascii_str}")
				print()

		pos += 1

	print(f"\nFound {len(found)} items with high quantities:")
	for name, qty, offset in found:
		print(f"  {name:40s} = {qty:6,}  at {offset}")


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print("="*78)
	print("SEARCHING FOR HIGH QUANTITY ITEMS IN itext_m_portland_6820")
	print("="*78)
	print()

	shop_id = 'itext_m_portland_6820'
	shop_pos = find_shop_position(data, shop_id)

	if shop_pos == -1:
		print(f"[ERROR] Shop '{shop_id}' not found!")
		exit(1)

	print(f"Shop ID found at offset: {shop_pos}")

	# Find sections
	garrison_pos = find_preceding_section(data, b'.garrison', shop_pos, 5000)
	items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
	units_pos = find_preceding_section(data, b'.shopunits', shop_pos, 5000)
	spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)

	print(f"\nSection positions:")
	if garrison_pos:
		print(f"  .garrison:  {garrison_pos}")
	print(f"  .items:     {items_pos}")
	print(f"  .shopunits: {units_pos}")
	print(f"  .spells:    {spells_pos}")
	print(f"  Shop ID:    {shop_pos}")

	# Scan entire shop region for high values
	start = garrison_pos if garrison_pos else items_pos
	scan_for_high_values(data, start, shop_pos)
