#!/usr/bin/env python3
"""Check if there's a field containing 818 near building_trader@31"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('CHECKING FOR ACTUAL TRADER NUMBER NEAR building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916

print(f'Position of "building_trader@31" text: {building_31_pos}')
print()

# Search for 818 as different integer formats in nearby area
target_num = 818

print('Searching for 818 stored as integer:')
print('-' * 80)
print()

# Check 1000 bytes before and after
search_start = max(0, building_31_pos - 1000)
search_end = min(len(data), building_31_pos + 1000)

# 1. As little-endian 2-byte integer
le_2byte = struct.pack('<H', target_num)
pos = data.find(le_2byte, search_start, search_end)
if pos != -1:
	offset = pos - building_31_pos
	print(f'✓ Found as 2-byte little-endian at position {pos} (offset {offset:+d})')

	# Show context
	context = data[max(0, pos-20):pos+20]
	print(f'  Hex: {context.hex()}')
	print(f'  ASCII: {context.decode("ascii", errors="ignore")}')
	print()

# 2. As little-endian 4-byte integer
le_4byte = struct.pack('<I', target_num)
pos = data.find(le_4byte, search_start, search_end)
if pos != -1:
	offset = pos - building_31_pos
	print(f'✓ Found as 4-byte little-endian at position {pos} (offset {offset:+d})')

	# Show context
	context = data[max(0, pos-20):pos+20]
	print(f'  Hex: {context.hex()}')
	print(f'  ASCII: {context.decode("ascii", errors="ignore")}')
	print()

# 3. Scan all 2-byte integers in the area
print('All 2-byte integers in range 100-2000 near building_trader@31:')
print('-' * 40)

for offset in range(-200, 200, 2):
	pos = building_31_pos + offset
	if pos + 2 <= len(data) and pos >= 0:
		value = struct.unpack('<H', data[pos:pos+2])[0]
		if 100 <= value <= 2000:
			print(f'  Offset {offset:+4d} (pos {pos}): {value}')
			if value == 818:
				print(f'    ★★★ THIS IS 818!')

print()
print('=' * 80)
print()

# Check the same for building_trader@818 in the lookup table
print('For comparison, checking building_trader@818 in lookup table:')
print('-' * 80)

lookup_818_pos = data.find(b'building_trader@818')
if lookup_818_pos != -1:
	print(f'Position of "building_trader@818" text: {lookup_818_pos}')
	print()

	# Check for 818 nearby
	search_start = max(0, lookup_818_pos - 200)
	search_end = min(len(data), lookup_818_pos + 200)

	le_2byte = struct.pack('<H', 818)
	pos = data.find(le_2byte, search_start, search_end)
	if pos != -1:
		offset = pos - lookup_818_pos
		print(f'Found 818 as 2-byte integer at offset {offset:+d}')
	else:
		print('818 NOT found as 2-byte integer nearby')

print()
print('=' * 80)
