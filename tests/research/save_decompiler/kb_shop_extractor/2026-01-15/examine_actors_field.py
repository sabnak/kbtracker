#!/usr/bin/env python3
"""Examine the .actors field after building_trader@31"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('EXAMINING .actors FIELD AFTER building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916

# Find .actors after building_trader@31
actors_pos = data.find(b'.actors', building_31_pos)

if actors_pos != -1 and actors_pos < building_31_pos + 500:
	print(f'Found .actors at position {actors_pos} (offset +{actors_pos - building_31_pos})')
	print()

	# Extract data after .actors
	chunk = data[actors_pos:actors_pos + 200]

	print('Hex dump of .actors section:')
	print(chunk.hex())
	print()

	print('ASCII decode:')
	print(chunk.decode('ascii', errors='ignore'))
	print()

	# Parse the structure
	print('Parsing .actors structure:')
	print('-' * 80)

	pos = len(b'.actors')

	# Try to read fields
	for i in range(10):
		if pos + 4 > len(chunk):
			break

		value = struct.unpack('<I', chunk[pos:pos+4])[0]
		print(f'  Offset +{pos:3d}: {value:12d} (0x{value:08x})')

		# Check if this is a reference to actor ID
		if value == 807991996:
			print(f'    ★★★ THIS IS ACTOR_807991996!')
		elif value > 100000000 and value < 3000000000:
			print(f'    (large number - could be actor ID)')

		pos += 4

	print()
else:
	print('No .actors field found near building_trader@31')

print()
print('=' * 80)
print()

# Compare with building_trader@818 in m_inselburg
print('For comparison, checking building_trader@818:')
print('-' * 80)

building_818_pos = data.find(b'building_trader@818')
if building_818_pos != -1:
	# Find if building_trader@818 in m_inselburg has a shop
	lt_search = data[max(0, building_818_pos - 500):building_818_pos]
	if b'm_inselburg' in lt_search:
		print('building_trader@818 in m_inselburg')

		actors_818 = data.find(b'.actors', building_818_pos)
		if actors_818 != -1 and actors_818 < building_818_pos + 500:
			print(f'Found .actors at position {actors_818}')

			chunk = data[actors_818:actors_818 + 100]
			print('Hex:', chunk[:50].hex())
			print('ASCII:', chunk.decode('ascii', errors='ignore')[:100])
	else:
		print('building_trader@818 is in lookup table, not actual shop')

print()
print('=' * 80)
