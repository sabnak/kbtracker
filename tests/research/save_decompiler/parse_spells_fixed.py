#!/usr/bin/env python3
"""
Fixed spell parser - scan entire section until shop ID
"""
import struct
import re
import os


def is_valid_spell(name: str) -> bool:
	"""Check if valid spell name"""
	if not name or len(name) < 5:
		return False
	return bool(re.match(r'^spell_[a-z0-9_]+$', name))


def parse_spells_fixed(data: bytes, section_pos: int, shop_pos: int) -> list:
	"""
	Parse spells from section_pos until shop_pos
	Scan through entire range looking for spell entries
	"""
	spells_dict = {}  # Use dict to dedupe and keep highest quantity

	# Scan from section start to shop ID
	pos = section_pos
	search_end = shop_pos

	print(f"Scanning from offset {section_pos} to {shop_pos} ({shop_pos - section_pos} bytes)")

	while pos < search_end - 20:
		# Try to read what looks like a spell entry:
		# 4 bytes length + name + 4 bytes quantity

		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			# Check if this could be a spell name length
			if 10 <= name_length <= 50:  # Reasonable spell name length
				if pos + 4 + name_length + 4 > len(data):
					pos += 1
					continue

				# Try to decode as ASCII
				try:
					spell_name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					# Check if it's a valid spell
					if is_valid_spell(spell_name):
						# Read quantity
						quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

						# Validate quantity (reasonable range)
						if 0 < quantity < 100:
							# Keep highest quantity if duplicate
							if spell_name not in spells_dict or spells_dict[spell_name] < quantity:
								spells_dict[spell_name] = quantity
								print(f"  Found: {spell_name} x{quantity} at offset {pos} (+{pos - section_pos} from section)")

							# Skip past this entry
							pos += 4 + name_length + 4
							continue

				except:
					pass

		except:
			pass

		# Move forward 1 byte
		pos += 1

	# Convert dict to sorted list
	return sorted([(name, qty) for name, qty in spells_dict.items()])


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	shop_pos = 630874
	spell_section_pos = 629793  # -1081 from shop

	print("Parsing spell section with fixed parser...")
	print("="*78)
	spells = parse_spells_fixed(data, spell_section_pos, shop_pos)

	print(f"\n{'='*78}")
	print(f"Total unique spells found: {len(spells)}")
	print(f"{'='*78}\n")

	# Display all spells
	for name, qty in spells:
		print(f"  {name} x{qty}")

	# Check for the specific spells user mentioned
	print(f"\n{'='*78}")
	print("Verifying user's first 8 spells:")
	print(f"{'='*78}")

	expected = {
		'spell_defenseless': 1,
		'spell_dispell': 4,
		'spell_empathy': 4,  # or spell_empathy2
		'spell_healing': 6,
		'spell_slow': 1,
		'spell_wasp_swarm': 1,
		'spell_cold_grasp': 2,
		'spell_scare': 3
	}

	spell_dict = {name: qty for name, qty in spells}

	all_found = True
	for spell, expected_qty in expected.items():
		if spell in spell_dict:
			actual_qty = spell_dict[spell]
			match = "OK" if actual_qty == expected_qty else f"qty mismatch: expected {expected_qty}, got {actual_qty}"
			print(f"  [OK] {spell} x{actual_qty} ({match})")
		else:
			print(f"  [MISS] {spell} NOT FOUND")
			all_found = False

	if all_found:
		print(f"\n[SUCCESS] All user-mentioned spells found!")
	else:
		print(f"\n[PARTIAL] Some spells missing")
