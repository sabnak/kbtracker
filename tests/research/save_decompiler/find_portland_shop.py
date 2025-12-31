#!/usr/bin/env python3
"""
Find and analyze shop itext_m_portland_6820 with crystal items
"""
import struct
import os


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


def hex_dump(data: bytes, offset: int, length: int) -> None:
	"""Print hex dump of data"""
	for i in range(0, length, 16):
		hex_part = ' '.join(f'{b:02x}' for b in data[offset+i:offset+i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset+i:offset+i+16])
		print(f"{offset+i:08x}: {hex_part:48s} {ascii_part}")


def search_items_section(data: bytes, items_pos: int, next_pos: int) -> None:
	"""Search items section for entries with various quantities"""
	print(f"\nSearching items from {items_pos} to {next_pos} ({next_pos - items_pos} bytes)")
	print()

	pos = items_pos + len(b'.items')
	search_end = next_pos

	found_items = []

	while pos < search_end - 20:
		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 5 <= name_length <= 100:
				if pos + 4 + name_length + 4 > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					if name.startswith(('crystal', 'mana', 'potion', 'scroll', 'elixir', 'addon')):
						# Read next few uint32 values
						values = []
						for i in range(6):
							offset = pos + 4 + name_length + (i * 4)
							if offset + 4 <= len(data):
								val = struct.unpack('<I', data[offset:offset+4])[0]
								values.append(val)

						found_items.append((name, pos, values))
						print(f"Found: {name:40s} at offset {pos}")
						print(f"  Next 6 uint32: {values}")

						# Hex dump
						dump_start = pos + 4 + name_length
						print(f"  Hex after name:")
						hex_bytes = data[dump_start:dump_start+24]
						print(f"    {' '.join(f'{b:02x}' for b in hex_bytes)}")
						print()

						pos += 4 + name_length + 4
						continue
				except:
					pass
		except:
			pass

		pos += 1

	if not found_items:
		print("[!] No crystal/consumable items found")
		print()
		print("Let me dump the first 200 bytes of items section to see the structure:")
		hex_dump(data, items_pos, 200)


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print("="*78)
	print("FINDING SHOP: itext_m_portland_6820")
	print("="*78)
	print()

	shop_id = 'itext_m_portland_6820'
	shop_pos = find_shop_position(data, shop_id)

	if shop_pos == -1:
		print(f"[ERROR] Shop '{shop_id}' not found!")
		exit(1)

	print(f"Shop ID found at offset: {shop_pos}")
	print()

	# Find sections
	items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
	spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)
	units_pos = find_preceding_section(data, b'.shopunits', shop_pos, 5000)

	print(f"Section positions:")
	print(f"  .items:     {items_pos if items_pos else 'NOT FOUND'}")
	print(f"  .shopunits: {units_pos if units_pos else 'NOT FOUND'}")
	print(f"  .spells:    {spells_pos if spells_pos else 'NOT FOUND'}")
	print(f"  Shop ID:    {shop_pos}")

	if items_pos:
		next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
		search_items_section(data, items_pos, next_pos)
