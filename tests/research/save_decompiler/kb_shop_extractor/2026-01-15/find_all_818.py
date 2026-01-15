#!/usr/bin/env python3
"""Find ALL occurrences of building_trader@818 and check their inventory"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('FINDING ALL building_trader@818 OCCURRENCES')
print('=' * 80)
print()

pattern = rb'building_trader@818(?!\d)'
matches = list(re.finditer(pattern, data))

print(f'Found {len(matches)} occurrences of building_trader@818')
print()

for i, match in enumerate(matches, 1):
	pos = match.start()
	print(f'{i}. Position {pos}:')

	# Check location
	search_before = data[max(0, pos - 500):pos]
	lt_pos = search_before.rfind(b'lt')
	if lt_pos != -1:
		try:
			import struct
			abs_lt_pos = max(0, pos - 500) + lt_pos
			length_bytes = data[abs_lt_pos + 2:abs_lt_pos + 6]
			if len(length_bytes) == 4:
				location_length = struct.unpack('<I', length_bytes)[0]
				if location_length < 100:
					location_start = abs_lt_pos + 6
					location_bytes = data[location_start:location_start + location_length]
					location = location_bytes.decode('ascii', errors='ignore')
					print(f'   Location: {location}')
		except:
			print(f'   Location: (could not extract)')
	else:
		print(f'   Location: (no lt tag found)')

	# Check for inventory before this position
	shopunits_search = data[max(0, pos - 1000):pos]
	if b'.shopunits' in shopunits_search:
		print(f'   Has .shopunits: YES')

		# Check for bocman
		if b'bocman' in shopunits_search:
			bocman_offset = shopunits_search.rfind(b'bocman')
			print(f'   ★★★ Contains BOCMAN! (offset {bocman_offset - 1000})')

			# Extract quantity
			try:
				# bocman/quantity/ format
				bocman_abs = max(0, pos - 1000) + bocman_offset
				chunk = data[bocman_abs:bocman_abs+20]
				text = chunk.decode('ascii', errors='ignore')
				qty_match = re.search(r'bocman/(\d+)', text)
				if qty_match:
					qty = int(qty_match.group(1))
					print(f'   Bocman quantity: {qty}')
			except:
				pass
	else:
		print(f'   Has .shopunits: NO (probably lookup table entry)')

	print()

print('=' * 80)
