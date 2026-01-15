#!/usr/bin/env python3
"""Test if offset of 787 works for all mappings"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('TESTING OFFSET THEORY: building_trader@(X-787) gets actor for @X')
print('=' * 80)
print()

# Extract lookup table mappings
lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

pattern = r'building_trader@(\d+).{1,50}se\D+(\d+)'
matches = list(re.finditer(pattern, text))

mappings = {}
for match in matches:
	building_num = int(match.group(1))
	actor_id = int(match.group(2))
	mappings[building_num] = actor_id

# Find all actual building_trader@ markers in save
actual_traders = set()
for match in re.finditer(rb'building_trader@(\d+)(?!\d)', data):
	num = int(match.group(1).decode('ascii'))
	# Skip if in lookup table area
	if not (2160000 <= match.start() <= 2180000):
		actual_traders.add(num)

print(f'Found {len(actual_traders)} actual building_trader@ in save (not in lookup table)')
print(f'Found {len(mappings)} mappings in lookup table')
print()

# Apply offset correction
OFFSET = 787

corrected_mappings = {}
for table_num, actor_id in mappings.items():
	correct_num = table_num - OFFSET
	corrected_mappings[correct_num] = actor_id

print('Corrected mappings (table_num - 787 = correct_num):')
print('-' * 80)
print()

# Show examples
examples = [31, 106, 293, 361]
for num in examples:
	if num in corrected_mappings:
		print(f'building_trader@{num} -> actor_{corrected_mappings[num]}')

print()
print('=' * 80)
print()

# Check building_trader@106 (should have actor_1049716918 if theory is correct)
print('Verifying building_trader@106:')
print('-' * 80)

pos_106 = None
for match in re.finditer(rb'building_trader@106(?!\d)', data):
	if not (2160000 <= match.start() <= 2180000):
		pos_106 = match.start()
		break

if pos_106:
	print(f'Found building_trader@106 at position {pos_106}')

	# Extract location
	search_start = max(0, pos_106 - 500)
	chunk_local = data[search_start:pos_106]
	lt_pos = chunk_local.rfind(b'lt')

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
					print(f'Location: {location}')
		except:
			pass

	print()
	print(f'If offset theory is correct:')
	print(f'  building_trader@106 should have actor_{corrected_mappings.get(106, "NOT IN TABLE")}')
	print(f'  (because lookup table says building_trader@893 -> actor_{mappings.get(893, "N/A")})')
else:
	print('building_trader@106 NOT FOUND in save file')

print()
print('=' * 80)
print()

# Summary
print('SUMMARY:')
print('-' * 80)
print()
print(f'Offset value: {OFFSET}')
print()
print('Verified examples:')
print(f'  ✓ building_trader@818 - {OFFSET} = 31 -> actor_807991996')
print(f'  ? building_trader@893 - {OFFSET} = 106 -> actor_1049716918 (needs verification)')
print()
print('To get correct mappings:')
print('  correct_building_num = lookup_table_building_num - 787')
print()
print('=' * 80)
