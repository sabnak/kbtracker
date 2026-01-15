#!/usr/bin/env python3
"""Find all exact occurrences of building_trader@31 in the save file"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('FINDING ALL OCCURRENCES OF building_trader@31')
print('=' * 80)
print()

# Use word boundary to match EXACT @31, not @318, @310, etc.
# Pattern: building_trader@31 followed by a non-digit character
pattern = rb'building_trader@31(?!\d)'

matches = list(re.finditer(pattern, data))

print(f'Found {len(matches)} exact occurrences of building_trader@31')
print()

for i, match in enumerate(matches, 1):
	pos = match.start()
	print(f'{i}. Position: {pos}')

	# Extract location from 'lt' tag before this position
	search_start = max(0, pos - 500)
	chunk = data[search_start:pos]
	lt_pos = chunk.rfind(b'lt')

	location = 'unknown'
	if lt_pos != -1:
		abs_lt_pos = search_start + lt_pos
		# Try to extract location
		try:
			import struct
			length_bytes = data[abs_lt_pos + 2:abs_lt_pos + 6]
			if len(length_bytes) == 4:
				location_length = struct.unpack('<I', length_bytes)[0]
				if location_length < 100:
					location_start = abs_lt_pos + 6
					location_bytes = data[location_start:location_start + location_length]
					location = location_bytes.decode('ascii', errors='ignore')
		except:
			pass

	print(f'   Location: {location}')

	# Check for inventory before this position
	shopunits_search = data[pos - 1000:pos]
	if b'.shopunits' in shopunits_search:
		print(f'   Has .shopunits nearby: YES')

		# Try to find bocman
		if b'bocman' in shopunits_search:
			bocman_offset = shopunits_search.find(b'bocman')
			print(f'   Contains bocman: YES (at offset {bocman_offset - 1000})')
	else:
		print(f'   Has .shopunits nearby: NO')

	# Show surrounding context
	context_start = max(0, pos - 100)
	context_end = min(len(data), pos + 100)
	context = data[context_start:context_end]
	context_ascii = context.decode('ascii', errors='ignore')

	print(f'   Context:')
	print(f'   {context_ascii}')
	print()

print('=' * 80)
