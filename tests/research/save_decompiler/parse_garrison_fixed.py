#!/usr/bin/env python3
"""
Parse garrison - units stored in format: unit/qty/unit/qty/...
"""
import struct
import os


def parse_garrison_string(data: bytes, garrison_pos: int, items_pos: int) -> list:
	"""
	Parse garrison section

	Garrison stores units as a string: "unit1/qty1/unit2/qty2/..."
	"""
	pos = garrison_pos + len(b'.garrison')

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, items_pos)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4

	# Read string length
	if pos + 4 > len(data):
		return []

	str_length = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	if str_length <= 0 or str_length > 500:
		return []

	if pos + str_length > len(data):
		return []

	# Read garrison string
	try:
		garrison_str = data[pos:pos+str_length].decode('ascii')
		print(f"Garrison string: '{garrison_str}'")

		# Parse format: unit/qty/unit/qty/...
		parts = garrison_str.split('/')

		units = []
		i = 0
		while i < len(parts) - 1:
			unit_name = parts[i]
			try:
				quantity = int(parts[i + 1])
				units.append((unit_name, quantity))
				print(f"  {unit_name} x{quantity}")
				i += 2
			except:
				i += 1

		return units

	except Exception as e:
		print(f"Error: {e}")
		return []


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	shop_pos = 630874
	garrison_pos = 627802
	items_pos = 627891

	print("Parsing garrison section...")
	print("="*78)
	garrison = parse_garrison_string(data, garrison_pos, items_pos)

	print(f"\n{'='*78}")
	print(f"Garrison slots used: {len(garrison)}/3")
	print(f"{'='*78}\n")

	if garrison:
		print("Units in garrison:")
		for name, qty in garrison:
			print(f"  {name:20s} x{qty}")
	else:
		print("  (empty)")
