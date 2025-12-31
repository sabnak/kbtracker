#!/usr/bin/env python3
"""
Compare binary structure of stackable (crystal) vs non-stackable (ring) items
"""
import struct
import os


def dump_item_structure(data: bytes, item_name: str) -> None:
	"""Find and dump item structure"""
	item_bytes = item_name.encode('ascii')
	pos = 0

	print(f"\n{'='*78}")
	print(f"ITEM: {item_name}")
	print(f"{'='*78}\n")

	occurrences = []
	while True:
		pos = data.find(item_bytes, pos)
		if pos == -1:
			break
		# Check if valid (preceded by length)
		try:
			length = struct.unpack('<I', data[pos-4:pos])[0]
			if length == len(item_bytes):
				occurrences.append(pos)
		except:
			pass
		pos += 1

	if not occurrences:
		print(f"Not found!")
		return

	print(f"Found {len(occurrences)} occurrences")

	# Use the one in shop section (around offset 392000-394000)
	shop_occurrence = None
	for pos in occurrences:
		if 392000 <= pos <= 394000:
			shop_occurrence = pos
			break

	if not shop_occurrence:
		shop_occurrence = occurrences[0]

	pos = shop_occurrence
	print(f"Analyzing occurrence at offset {pos}")
	print()

	# Structure after name
	after_name = pos + len(item_bytes)
	print("First 15 uint32 values after name:")
	for i in range(15):
		offset = after_name + (i * 4)
		if offset + 4 <= len(data):
			val = struct.unpack('<I', data[offset:offset+4])[0]
			hex_bytes = ' '.join(f'{b:02x}' for b in data[offset:offset+4])

			# Try to interpret
			interpretation = ""
			if val == 3:
				interpretation = " <- possibly metadata marker"
			elif val == 4:
				interpretation = " <- quantity? or metadata?"
			elif val == 5:
				interpretation = " <- possibly string length"
			elif 32 <= val < 127:
				interpretation = f" <- ASCII '{chr(val)}'"

			print(f"  +{i*4:3d}: {val:10d} (0x{val:08x}) [{hex_bytes}]{interpretation}")

	# Check for embedded strings
	print("\nEmbedded strings after name:")
	scan_pos = after_name
	found_strings = []
	for _ in range(100):
		try:
			str_len = struct.unpack('<I', data[scan_pos:scan_pos+4])[0]
			if 1 <= str_len <= 50:
				try:
					maybe_str = data[scan_pos+4:scan_pos+4+str_len].decode('ascii', errors='strict')
					offset_from_name = scan_pos - after_name
					print(f"  +{offset_from_name:3d}: length={str_len:2d}, string='{maybe_str}'")
					found_strings.append((offset_from_name, maybe_str))
					scan_pos += 4 + str_len
					continue
				except:
					pass
		except:
			pass
		scan_pos += 1
		if scan_pos > after_name + 200:
			break

	# Full hex dump
	print(f"\nFull hex dump (100 bytes after name):")
	dump_start = after_name
	for i in range(0, 100, 16):
		offset = dump_start + i
		hex_part = ' '.join(f'{b:02x}' for b in data[offset:offset+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset:offset+16])
		print(f"  {offset:08x}: {hex_part:48s} {ascii_part}")


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print("="*78)
	print("COMPARING STACKABLE VS NON-STACKABLE ITEMS")
	print("="*78)

	# Stackable (crystal - should have qty=4)
	dump_item_structure(data, 'addon4_3_crystal')

	# Non-stackable equipment (ring - should have qty=1)
	dump_item_structure(data, 'snake_ring')

	# Another equipment item
	dump_item_structure(data, 'straw_hat')

	# Another equipment item
	dump_item_structure(data, 'addon4_human_bowman_guild_regalia')
