#!/usr/bin/env python3
"""Show full content of .actors field for building_trader@31"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('FULL CONTENT OF .actors FIELD FOR building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916
actors_pos = data.find(b'.actors', building_31_pos)

if actors_pos != -1:
	print(f'.actors position: {actors_pos}')
	print()

	# Find the end of .actors section (next section marker or end of structure)
	section_markers = [b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp', b'building_', b'itext_']

	# Search for next section
	end_pos = actors_pos + 1000  # default max
	for marker in section_markers:
		next_pos = data.find(marker, actors_pos + 10)
		if next_pos != -1 and next_pos < end_pos:
			end_pos = next_pos

	actors_content = data[actors_pos:end_pos]

	print(f'Section length: {len(actors_content)} bytes')
	print()

	print('=' * 80)
	print('HEX DUMP:')
	print('=' * 80)
	print(actors_content.hex())
	print()

	print('=' * 80)
	print('ASCII DECODE:')
	print('=' * 80)
	print(actors_content.decode('ascii', errors='ignore'))
	print()

	print('=' * 80)
	print('LOOKING FOR LARGE NUMBERS (potential actor IDs):')
	print('=' * 80)
	print()

	# Scan all 4-byte integers in this section
	for offset in range(0, len(actors_content) - 4):
		value = struct.unpack('<I', actors_content[offset:offset+4])[0]

		# Check if this could be an actor ID (8-9 digit number)
		if 100000000 <= value <= 2999999999:
			print(f'Offset +{offset:3d} (pos {actors_pos + offset}): {value}')

			# Check if it matches our target
			if value == 807991996:
				print(f'  ★★★ THIS IS actor_807991996!')

			# Check if it matches any dragondor actor
			dragondor_actors = [110905037, 1167461685, 1815772648, 608572288, 807991996, 886465971]
			if value in dragondor_actors:
				print(f'  ✓ This is a dragondor actor!')

	print()
	print('=' * 80)

else:
	print('No .actors field found')
