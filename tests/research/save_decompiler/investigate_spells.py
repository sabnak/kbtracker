#!/usr/bin/env python3
"""
Investigate spell data structure in save files
"""
import struct
import os


def find_shop_section(data: bytes, shop_id: str) -> int:
	"""Find the position of a specific shop by ID"""
	shop_bytes = shop_id.encode('utf-16-le')
	pos = data.find(shop_bytes)
	return pos if pos != -1 else None


def find_all_spells_sections(data: bytes) -> list:
	"""Find all .spells sections"""
	sections = []
	pos = 0

	while True:
		pos = data.find(b'.spells', pos)
		if pos == -1:
			break
		sections.append(pos)
		pos += 1

	return sections


def find_spells_sections_near(data: bytes, shop_pos: int, search_range: int = 16384):
	"""Find .spells sections near shop ID"""
	search_start = max(0, shop_pos - search_range)
	search_end = min(len(data), shop_pos + search_range)

	sections = []
	pos = search_start

	while True:
		spells_pos = data.find(b'.spells', pos, search_end)
		if spells_pos == -1:
			break

		sections.append(spells_pos)
		pos = spells_pos + 1

	return sections


def hex_dump(data: bytes, start: int, length: int = 256, highlight_pos: int = None):
	"""Print hex dump"""
	for i in range(0, length, 16):
		offset = start + i
		if offset >= len(data):
			break

		chunk = data[offset:offset+16]
		hex_part = ' '.join(f'{b:02X}' for b in chunk).ljust(48)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)

		marker = '>>>' if highlight_pos and start + i <= highlight_pos < start + i + 16 else '   '
		print(f"{marker} {offset:08X}  {hex_part}  {ascii_part}")


def parse_spells_section(data: bytes, section_pos: int):
	"""Try to parse spells section"""
	print(f"\n{'='*78}")
	print(f"Parsing .spells section at offset {section_pos} (0x{section_pos:X})")
	print(f"{'='*78}")

	# Show hex dump around .spells marker
	print("\nHex dump around .spells marker:")
	hex_dump(data, section_pos - 32, 512)

	pos = section_pos + len(b'.spells')

	# Try to find 'strg' marker like in .items
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos != -1:
		print(f"\nFound 'strg' marker at offset {strg_pos} (0x{strg_pos:X})")
		pos = strg_pos + 4

		# Read count
		if pos + 4 <= len(data):
			spell_count = struct.unpack('<I', data[pos:pos+4])[0]
			print(f"Possible spell count: {spell_count}")
			pos += 4

			# Show next bytes
			print(f"\nNext 128 bytes after count:")
			hex_dump(data, pos, 128)

			# Try to parse spells
			print(f"\nAttempting to parse spells...")
			pos += 8  # Skip metadata like in items

			for i in range(min(spell_count, 50)):
				if pos + 4 > len(data):
					break

				spell_length = struct.unpack('<I', data[pos:pos+4])[0]
				print(f"\n[{i}] Length: {spell_length} at offset {pos}")

				if spell_length <= 0 or spell_length > 200:
					print(f"    Invalid length, stopping")
					break

				pos += 4

				if pos + spell_length > len(data):
					break

				try:
					spell_name = data[pos:pos+spell_length].decode('ascii', errors='strict')
					print(f"    Name: '{spell_name}'")

					# Check if there's a count/quantity after the name
					spell_end = pos + spell_length
					print(f"    Bytes after name: {data[spell_end:spell_end+20].hex()}")

					# Try to read potential quantity
					if spell_end + 4 <= len(data):
						possible_count = struct.unpack('<I', data[spell_end:spell_end+4])[0]
						print(f"    Possible count: {possible_count}")

					pos += spell_length

					# Look for next spell
					max_skip = 200
					found_next = False
					for skip in range(max_skip):
						if pos + skip + 4 > len(data):
							break

						next_len = struct.unpack('<I', data[pos+skip:pos+skip+4])[0]
						if 5 <= next_len <= 100:
							try:
								test_name = data[pos+skip+4:pos+skip+4+min(next_len, 50)].decode('ascii', errors='strict')
								if '_' in test_name and test_name[0].isalpha():
									print(f"    Next spell at +{skip} bytes")
									pos += skip
									found_next = True
									break
							except:
								pass

					if not found_next:
						print(f"    No more spells found")
						break

				except Exception as e:
					print(f"    Error: {e}")
					break


def investigate_shop_spells(data: bytes, shop_id: str):
	"""Investigate spell sections for a specific shop"""
	print(f"Investigating spells for shop: {shop_id}")
	print("=" * 78)

	# Find shop
	shop_pos = find_shop_section(data, shop_id)
	if shop_pos is None:
		print(f"Shop {shop_id} not found!")
		return

	print(f"\nShop ID found at offset: {shop_pos} (0x{shop_pos:X})")

	# Find .spells sections near this shop
	spells_sections = find_spells_sections_near(data, shop_pos)
	print(f"\nFound {len(spells_sections)} .spells sections within 16KB range:")

	for i, section_pos in enumerate(spells_sections):
		distance = section_pos - shop_pos
		print(f"\n{'='*78}")
		print(f"Section {i+1}: Offset {section_pos} (0x{section_pos:X})")
		print(f"Distance from shop: {distance:+d} bytes")

		parse_spells_section(data, section_pos)


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	print("Loading decompressed save data...\n")
	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# First, show overall statistics
	all_spells_sections = find_all_spells_sections(data)
	print(f"Total .spells sections in save file: {len(all_spells_sections)}\n")

	# Investigate the specific shop
	investigate_shop_spells(data, 'itext_m_zcom_1422')
