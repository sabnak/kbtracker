#!/usr/bin/env python3
"""Examine the .actors section BEFORE the inventory"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('.actors SECTION BEFORE INVENTORY (position 669357)')
print('=' * 80)
print()

actors_before_pos = 669357

# Extract full section (until next section marker)
next_section_pos = data.find(b'.shopunits', actors_before_pos)
if next_section_pos == -1:
	next_section_pos = actors_before_pos + 200

section_content = data[actors_before_pos:next_section_pos]

print(f'Section length: {len(section_content)} bytes')
print()

print('HEX DUMP:')
print('-' * 80)
print(section_content.hex())
print()

print('ASCII DECODE:')
print('-' * 80)
print(section_content.decode('ascii', errors='ignore'))
print()

print('=' * 80)
print('PARSING STRUCTURE:')
print('=' * 80)
print()

# Parse byte by byte
pos = 7  # Skip ".actors"

# Read values
for i in range(20):
	if pos + 4 > len(section_content):
		break

	value = struct.unpack('<I', section_content[pos:pos+4])[0]

	print(f'Offset +{pos:3d}: {value:12d} (0x{value:08x})', end='')

	# Check if this is actor_807991996
	if value == 807991996:
		print(f' ★★★ THIS IS actor_807991996!')
	elif value > 100000000 and value < 3000000000:
		print(f' (large - could be actor ID)')

		# Check if it matches any dragondor actor
		dragondor_actors = [110905037, 1167461685, 1815772648, 608572288, 807991996, 886465971]
		if value in dragondor_actors:
			print(f'       ✓ This IS a dragondor actor!')
	else:
		print()

	pos += 4

print()
print('=' * 80)
print()

# Show the strg value specifically
print('Extracting strg value:')
print('-' * 80)

strg_pos = section_content.find(b'strg')
if strg_pos != -1:
	# strg marker (4) + length (4) + value (4)
	value_pos = strg_pos + 8
	if value_pos + 4 <= len(section_content):
		strg_value = struct.unpack('<I', section_content[value_pos:value_pos+4])[0]
		print(f'strg value: {strg_value} (0x{strg_value:08x})')

		if strg_value == 807991996:
			print(f'★★★ THIS IS actor_807991996!')

print()
print('=' * 80)
