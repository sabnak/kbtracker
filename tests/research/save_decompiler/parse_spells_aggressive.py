#!/usr/bin/env python3
"""
Parse ALL spells from section - aggressive approach
Don't stop on first failure, keep searching
"""
import struct
import os


def is_valid_spell(name: str) -> bool:
	"""Check if valid spell name"""
	if not name or len(name) < 5:
		return False
	import re
	return bool(re.match(r'^spell_[a-z0-9_]+$', name))


def parse_spells_aggressive(data: bytes, section_pos: int) -> list:
	"""
	Aggressively parse spells - don't stop on first gap
	Search through entire reasonable range
	"""
	spells = []
	pos = section_pos + len(b'.spells')

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, pos + 200)
	if strg_pos == -1:
		return []

	# Start after strg + count + metadata
	pos = strg_pos + 4 + 4 + 8

	# Search through next 5KB for spell entries
	search_end = min(pos + 5000, len(data))

	while pos < search_end - 100:
		# Try to read a length at current position
		if pos + 4 > len(data):
			break

		try:
			spell_length = struct.unpack('<I', data[pos:pos+4])[0]

			# Check if this looks like a valid spell entry
			if 10 <= spell_length <= 100:  # Reasonable spell name length
				if pos + 4 + spell_length + 4 > len(data):
					pos += 1
					continue

				# Try to decode spell name
				try:
					spell_name = data[pos+4:pos+4+spell_length].decode('ascii', errors='strict')

					# Check if it's a valid spell name
					if is_valid_spell(spell_name):
						# Read quantity
						quantity = struct.unpack('<I', data[pos+4+spell_length:pos+4+spell_length+4])[0]

						# Validate quantity
						if 0 < quantity < 10000:
							spells.append((spell_name, quantity))
							print(f"Found: {spell_name} x{quantity} at offset {pos}")

							# Jump past this entry
							pos += 4 + spell_length + 100  # Skip past metadata
							continue

				except:
					pass

		except:
			pass

		# Move to next byte
		pos += 1

	return spells


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# The spell section at -1081 bytes from shop
	shop_pos = 630874
	spell_section_pos = 629793  # shop_pos - 1081

	print("Aggressively parsing spell section...")
	print("="*78)
	spells = parse_spells_aggressive(data, spell_section_pos)

	print(f"\n{'='*78}")
	print(f"Total spells found: {len(spells)}")
	print(f"{'='*78}\n")

	# Sort and display
	for name, qty in sorted(spells):
		print(f"  {name} x{qty}")

	# Check for the specific spells user mentioned
	print(f"\n{'='*78}")
	print("Checking user's first 8 spells:")
	print(f"{'='*78}")

	expected = [
		'spell_defenseless',
		'spell_dispell',
		'spell_empathy',
		'spell_healing',
		'spell_slow',
		'spell_wasp_swarm',
		'spell_cold_grasp',
		'spell_scare'
	]

	spell_dict = {name: qty for name, qty in spells}

	for spell in expected:
		if spell in spell_dict:
			print(f"  ✓ {spell} x{spell_dict[spell]}")
		else:
			print(f"  ✗ {spell} NOT FOUND")
