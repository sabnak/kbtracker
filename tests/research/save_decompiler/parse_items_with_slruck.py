#!/usr/bin/env python3
"""
Parse items by reading quantity from slruck field
"""
import struct
import re
import os


def parse_items_correct(data: bytes, section_pos: int, next_pos: int) -> list:
	"""
	Parse items section correctly by reading quantity from slruck field
	"""
	items = []
	pos = section_pos + len(b'.items')
	search_end = next_pos

	metadata_keywords = {'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid'}

	while pos < search_end - 20:
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

					# Validate ID
					if not re.match(r'^[a-z][a-z0-9_]*$', name):
						pos += 1
						continue

					# Skip metadata keywords
					if name in metadata_keywords:
						pos += 4 + name_length
						continue

					# Skip if too short
					if len(name) < 5:
						pos += 1
						continue

					# Found valid item name! Now scan forward for slruck field
					scan_pos = pos + 4 + name_length
					quantity = 1  # Default

					# Scan next 200 bytes for slruck
					for _ in range(50):
						if scan_pos + 10 > search_end:
							break

						# Look for "slruck" string (6 bytes)
						if data[scan_pos:scan_pos+6] == b'slruck':
							# slruck format: [6-byte-string][uint32-length][string-content]
							try:
								# Read length of the value
								val_len = struct.unpack('<I', data[scan_pos+6:scan_pos+10])[0]
								if 1 <= val_len <= 20:
									val_str = data[scan_pos+10:scan_pos+10+val_len].decode('ascii', errors='strict')
									# Parse "slot,qty" format
									if ',' in val_str:
										parts = val_str.split(',')
										if len(parts) == 2:
											try:
												quantity = int(parts[1])
												break
											except:
												pass
							except:
								pass

						scan_pos += 1

					items.append((name, quantity))
					pos += 4 + name_length
					continue

				except:
					pass
		except:
			pass

		pos += 1

	return sorted(items, key=lambda x: x[0])


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Find portland_6820
	shop_id = 'itext_m_portland_6820'
	shop_bytes = shop_id.encode('utf-16-le')
	shop_pos = data.find(shop_bytes)

	print("="*78)
	print(f"PARSING ITEMS WITH CORRECT QUANTITY (from slruck field)")
	print("="*78)
	print()

	# Find sections
	def find_section(marker):
		search_start = max(0, shop_pos - 5000)
		chunk = data[search_start:shop_pos]
		offset = chunk.rfind(marker)
		return search_start + offset if offset != -1 else None

	items_pos = find_section(b'.items')
	units_pos = find_section(b'.shopunits')
	spells_pos = find_section(b'.spells')

	print(f"Shop: {shop_id} at offset {shop_pos}")
	print(f"Items section at: {items_pos}")
	print()

	if items_pos:
		next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
		items = parse_items_correct(data, items_pos, next_pos)

		print(f"Items found: {len(items)}")
		print()
		for name, qty in items:
			print(f"  {name:45s} qty={qty}")
