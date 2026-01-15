#!/usr/bin/env python3
"""Check building_trader@893 mapping (should be wrong according to user)"""

from pathlib import Path

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('CHECKING building_trader@893 MAPPING')
print('=' * 80)
print()

# Search for building_trader@893 in lookup table
pattern = b'building_trader@893'
pos = data.find(pattern)

if pos != -1:
	print(f'Found building_trader@893 at position {pos}')
	print()

	# Show context
	start = max(0, pos - 200)
	end = min(len(data), pos + 300)
	chunk = data[start:end]

	print('Context:')
	print(chunk.decode('ascii', errors='ignore'))
	print()
else:
	print('building_trader@893 NOT FOUND in lookup table')
	print()

# Search for actor_1049716918
print('=' * 80)
print('SEARCHING FOR actor_1049716918:')
print('=' * 80)
print()

actor_pattern = b'1049716918'
pos = data.find(actor_pattern)

if pos != -1:
	print(f'Found 1049716918 at position {pos}')
	print()

	# Show context
	start = max(0, pos - 300)
	end = min(len(data), pos + 200)
	chunk = data[start:end]

	print('Context:')
	print(chunk.decode('ascii', errors='ignore'))
	print()
else:
	print('1049716918 NOT FOUND')
	print()

# Also search for building_trader@893 in the actual save data (not lookup table)
print('=' * 80)
print('FINDING building_trader@893 IN ACTUAL SAVE DATA:')
print('=' * 80)
print()

import re
all_893 = []
for match in re.finditer(b'building_trader@893(?!\\d)', data):
	all_893.append(match.start())

print(f'Found {len(all_893)} occurrences of building_trader@893')
print()

for i, pos in enumerate(all_893, 1):
	print(f'{i}. Position {pos}:')

	# Extract location from lt tag
	search_start = max(0, pos - 500)
	chunk = data[search_start:pos]
	lt_pos = chunk.rfind(b'lt')

	if lt_pos != -1:
		try:
			import struct
			abs_lt_pos = search_start + lt_pos
			length_bytes = data[abs_lt_pos + 2:abs_lt_pos + 6]
			if len(length_bytes) == 4:
				location_length = struct.unpack('<I', length_bytes)[0]
				if location_length < 100:
					location_start = abs_lt_pos + 6
					location_bytes = data[location_start:location_start + location_length]
					location = location_bytes.decode('ascii', errors='ignore')
					print(f'   Location: {location}')
		except:
			pass

	# Check for shopunits
	if b'.shopunits' in data[pos - 1000:pos]:
		print(f'   Has inventory: YES')
	else:
		print(f'   Has inventory: NO (probably lookup table entry)')

	print()

print('=' * 80)
