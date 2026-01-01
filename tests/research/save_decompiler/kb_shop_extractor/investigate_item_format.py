#!/usr/bin/env python3
"""
Investigate item vs spell binary format differences
"""
import struct
import os


def hex_dump(data: bytes, offset: int, length: int) -> None:
	"""Print hex dump of data"""
	for i in range(0, length, 16):
		hex_part = ' '.join(f'{b:02x}' for b in data[offset+i:offset+i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset+i:offset+i+16])
		print(f"{offset+i:08x}: {hex_part:48s} {ascii_part}")


def find_and_dump_item(data: bytes, item_name: bytes, section_start: int, section_end: int) -> None:
	"""Find an item and dump surrounding bytes"""
	name_bytes = item_name
	pos = data.find(name_bytes, section_start, section_end)

	if pos == -1:
		print(f"  Not found: {item_name}")
		return

	# Look backwards for length field
	search_back = 20
	for back in range(search_back):
		test_pos = pos - 4 - back
		if test_pos < 0:
			break

		try:
			length = struct.unpack('<I', data[test_pos:test_pos+4])[0]
			if length == len(name_bytes):
				print(f"\n  Found '{item_name}' at offset {pos} (length field at {test_pos}):")
				print(f"  Structure: [4-byte-length][{length}-byte-name][???]")

				# Dump bytes after name
				dump_start = pos + len(name_bytes)
				print(f"\n  Bytes after name:")
				hex_dump(data, dump_start, 64)

				# Try reading as uint32
				if dump_start + 4 <= len(data):
					val1 = struct.unpack('<I', data[dump_start:dump_start+4])[0]
					val2 = struct.unpack('<I', data[dump_start+4:dump_start+8])[0] if dump_start + 8 <= len(data) else 0
					val3 = struct.unpack('<I', data[dump_start+8:dump_start+12])[0] if dump_start + 12 <= len(data) else 0
					print(f"\n  Next uint32 values: {val1}, {val2}, {val3}")

				return
		except:
			pass

	print(f"  Found '{item_name}' at {pos} but couldn't find length field")


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Test shop positions
	shop_pos = 630874
	items_pos = 627891
	spells_pos = 629793

	print("="*78)
	print("INVESTIGATING ITEM vs SPELL FORMAT")
	print("="*78)

	print("\n--- ITEMS SECTION ---")
	print("Testing equipment item (should have qty=1 in game):")
	find_and_dump_item(data, b'addon4_dwarf_simple_belt', items_pos, spells_pos)

	print("\n\nTesting another equipment item:")
	find_and_dump_item(data, b'tournament_helm', items_pos, spells_pos)

	print("\n\n--- SPELLS SECTION ---")
	print("Testing spell with qty=1:")
	find_and_dump_item(data, b'spell_blind', spells_pos, shop_pos)

	print("\n\nTesting spell with qty=2:")
	find_and_dump_item(data, b'spell_chaos_coagulate', spells_pos, shop_pos)

	print("\n\nTesting spell with qty=6:")
	find_and_dump_item(data, b'spell_healing', spells_pos, shop_pos)
