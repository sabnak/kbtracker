#!/usr/bin/env python3
"""
Parse units (.shopunits) section for test shop
"""
import struct
import re
import os


def is_valid_unit(name: str) -> bool:
	"""Check if valid unit name"""
	if not name or len(name) < 3:
		return False
	return bool(re.match(r'^[a-z][a-z0-9_]*$', name))


def parse_units_section(data: bytes, section_pos: int, next_section_pos: int) -> list:
	"""Parse units section - same format as items/spells"""
	units = {}

	print(f"Scanning units from {section_pos} to {next_section_pos} ({next_section_pos - section_pos} bytes)")

	pos = section_pos + len(b'.shopunits')
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
								print(f"  Found: {unit_name} x{quantity} at offset {pos} (+{pos - section_pos})")

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
	shopunits_pos = 629039
	spells_pos = 629793  # Next section

	print("Parsing .shopunits section...")
	print("="*78)
	units = parse_units_section(data, shopunits_pos, spells_pos)

	print(f"\n{'='*78}")
	print(f"Units found: {len(units)}")
	print(f"{'='*78}\n")

	if units:
		for name, qty in units:
			print(f"  {name} x{qty}")
	else:
		print("  (empty or no units for sale)")
