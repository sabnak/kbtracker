#!/usr/bin/env python3
"""
Debug the spell section parsing in detail
"""
import struct
import os


def hex_dump(data: bytes, start: int, length: int):
	"""Print hex dump"""
	for i in range(0, length, 16):
		offset = start + i
		if offset >= len(data):
			break

		chunk = data[offset:offset+16]
		hex_part = ' '.join(f'{b:02X}' for b in chunk).ljust(48)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
		print(f"{offset:08X}  {hex_part}  {ascii_part}")


def debug_spell_section(data: bytes, section_pos: int):
	"""Debug spell section parsing"""
	print(f"Debugging .spells section at offset {section_pos} (0x{section_pos:X})")
	print(f"{'='*78}\n")

	pos = section_pos + len(b'.spells')

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		print("ERROR: No 'strg' marker found!")
		return

	print(f"'strg' marker at offset {strg_pos} (0x{strg_pos:X})")
	pos = strg_pos + 4

	# Read count
	spell_count = struct.unpack('<I', data[pos:pos+4])[0]
	print(f"Spell count in header: {spell_count}")
	pos += 4

	print(f"\nMetadata bytes: {data[pos:pos+8].hex()}")
	pos += 8

	print(f"\nStarting spell parsing at offset {pos} (0x{pos:X})")
	print(f"{'='*78}\n")

	# Parse ALL spells with detailed logging
	spells_found = []
	for i in range(200):  # Try to parse up to 200 spells
		if pos + 4 > len(data):
			print(f"[{i}] ERROR: Not enough data for length field")
			break

		# Read length
		spell_length = struct.unpack('<I', data[pos:pos+4])[0]

		if spell_length <= 0 or spell_length > 200:
			print(f"[{i}] Invalid length {spell_length}, stopping")
			break

		pos += 4

		if pos + spell_length > len(data):
			print(f"[{i}] ERROR: Not enough data for spell name")
			break

		# Read spell name
		try:
			spell_name = data[pos:pos+spell_length].decode('ascii', errors='strict')
			pos += spell_length

			# Read quantity
			if pos + 4 <= len(data):
				quantity = struct.unpack('<I', data[pos:pos+4])[0]
			else:
				quantity = 0

			# Check if valid
			is_valid = spell_name and '_' in spell_name and spell_name[0].isalpha()

			if is_valid and quantity > 0 and quantity < 10000:
				spells_found.append((spell_name, quantity))
				print(f"[{i}] ✓ {spell_name} x{quantity}")
			else:
				print(f"[{i}] ✗ '{spell_name}' qty={quantity} (invalid, stopping)")
				break

			# Try to find next spell
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
							pos += skip
							found_next = True
							break
					except:
						pass

			if not found_next:
				print(f"\n[{i}] No more spells found after searching {max_skip} bytes")
				print(f"Last position: {pos} (0x{pos:X})")
				print(f"\nHex dump of next 256 bytes:")
				hex_dump(data, pos, 256)
				break

		except Exception as e:
			print(f"[{i}] ERROR: {e}")
			break

	print(f"\n{'='*78}")
	print(f"Total spells parsed: {len(spells_found)}")
	print(f"Expected from header: {spell_count}")
	print(f"{'='*78}")

	return spells_found


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# The spell section at -1081 bytes from shop
	shop_pos = 630874
	spell_section_pos = 629793  # shop_pos - 1081

	spells = debug_spell_section(data, spell_section_pos)
