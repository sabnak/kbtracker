#!/usr/bin/env python3
"""
Search all shops for consumable items with high quantities (10k-50k)
"""
import struct
import re
import os


def find_all_shop_ids(data: bytes) -> list:
	"""Find all shop IDs in save file"""
	shops = []
	pos = 0
	while pos < len(data):
		chunk_size = 10000
		if pos + chunk_size > len(data):
			chunk_size = len(data) - pos

		try:
			text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
			matches = re.finditer(r'itext_m_\w+_\d+', text)

			for match in matches:
				shop_id = match.group(0)
				shop_bytes = shop_id.encode('utf-16-le')
				actual_pos = data.find(shop_bytes, pos, pos+chunk_size)
				if actual_pos != -1 and shop_id not in [s[0] for s in shops]:
					shops.append((shop_id, actual_pos))
		except:
			pass

		pos += chunk_size

	return sorted(shops, key=lambda x: x[1])


def find_preceding_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 5000) -> int:
	"""Find section marker immediately BEFORE shop ID"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos
	return None


def search_for_consumables(data: bytes, section_start: int, section_end: int, shop_id: str) -> list:
	"""Search for items with quantity in range 10000-50000"""
	pos = section_start
	found = []

	while pos < section_end - 20:
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

					if re.match(r'^[a-z][a-z0-9_]*$', name):
						# Read first uint32 after name
						quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

						# Check if it's in consumable range
						if 10000 <= quantity <= 50000:
							found.append((name, quantity, pos))
							pos += 4 + name_length + 4
							continue
				except:
					pass
		except:
			pass

		pos += 1

	return found


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	print("="*78)
	print("SEARCHING FOR CONSUMABLE ITEMS (quantity 10k-50k)")
	print("="*78)
	print()

	shops = find_all_shop_ids(data)
	print(f"Found {len(shops)} shops")
	print()

	all_consumables = []

	for shop_id, shop_pos in shops:
		items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
		spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)

		if items_pos:
			next_pos = spells_pos if spells_pos else shop_pos
			consumables = search_for_consumables(data, items_pos, next_pos, shop_id)

			if consumables:
				print(f"Shop: {shop_id}")
				for name, qty, pos in consumables:
					print(f"  {name:40s} qty={qty:6d}  at offset {pos}")
					all_consumables.append((shop_id, name, qty))
				print()

	print(f"\n{'='*78}")
	print(f"Total consumables found: {len(all_consumables)}")
