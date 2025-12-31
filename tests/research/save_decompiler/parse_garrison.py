#!/usr/bin/env python3
"""
Parse garrison section
"""
import struct
import re
import os


def is_valid_unit(name: str) -> bool:
	"""Check if valid unit name"""
	if not name or len(name) < 3:
		return False
	return bool(re.match(r'^[a-z][a-z0-9_]*$', name))


def parse_garrison(data: bytes, garrison_pos: int, next_section_pos: int) -> list:
	"""Parse garrison section - units stored by player"""
	units = {}

	print(f"Scanning garrison from {garrison_pos} to {next_section_pos} ({next_section_pos - garrison_pos} bytes)")

	pos = garrison_pos
	search_end = next_section_pos

	while pos < search_end - 20:
		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 5 <= name_length <= 50:
				if pos + 4 + name_length + 4 > len(data):
					pos += 1
					continue

				try:
					unit_name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					if is_valid_unit(unit_name):
						quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

						if 0 < quantity < 100000:
							if unit_name not in units or units[unit_name] < quantity:
								units[unit_name] = quantity
								print(f"  Found: {unit_name} x{quantity} at offset {pos} (+{pos - garrison_pos})")

							pos += 4 + name_length + 4
							continue

				except:
					pass

		except:
			pass

		pos += 1

	return sorted([(name, qty) for name, qty in units.items()])


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	shop_pos = 630874
	garrison_pos = 627802
	items_pos = 627891  # Next section

	print("Parsing garrison section...")
	print("="*78)
	garrison = parse_garrison(data, garrison_pos, items_pos)

	print(f"\n{'='*78}")
	print(f"Garrison units found: {len(garrison)}")
	print(f"{'='*78}\n")

	if garrison:
		for name, qty in garrison:
			print(f"  {name} x{qty}")
	else:
		print("  (empty)")

	print(f"\nNote: User mentioned garrison has max 3 slots")
	print(f"Found {len(garrison)} unit types")
