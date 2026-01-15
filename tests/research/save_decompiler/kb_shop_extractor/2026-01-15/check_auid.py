#!/usr/bin/env python3
"""Check auid fields near building_trader markers"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('CHECKING auid FIELDS NEAR BUILDING_TRADER MARKERS')
print('=' * 80)
print()

def extract_auid_after_marker(data: bytes, marker_pos: int, marker_name: str):
	"""Extract auid value that comes after a building_trader marker"""
	# Look for 'auid' in the next 200 bytes
	search_end = min(len(data), marker_pos + 200)
	chunk = data[marker_pos:search_end]

	auid_pos = chunk.find(b'auid')
	if auid_pos == -1:
		print(f'  {marker_name}: No auid found')
		return None

	abs_auid_pos = marker_pos + auid_pos
	print(f'  {marker_name}: auid at position {abs_auid_pos} (offset +{auid_pos})')

	# auid is followed by 1 byte flag, then 4 bytes little-endian integer
	# Pattern: 'auid' + byte + 4-byte value
	value_offset = auid_pos + 5  # 'auid' (4 bytes) + flag (1 byte)

	if value_offset + 4 <= len(chunk):
		value_bytes = chunk[value_offset:value_offset + 4]
		value = struct.unpack('<I', value_bytes)[0]
		print(f'    Value: {value}')

		# Show surrounding context
		context_start = max(0, auid_pos - 20)
		context_end = min(len(chunk), auid_pos + 40)
		context = chunk[context_start:context_end]
		print(f'    Context (hex): {context.hex()}')
		print(f'    Context (ascii): {context.decode("ascii", errors="ignore")}')

		return value
	else:
		print(f'    Cannot read value (not enough bytes)')
		return None

print()

# Check building_trader@31
print('1. building_trader@31 (the missing shop with bocman):')
pos_31 = data.find(b'building_trader@31')
if pos_31 != -1:
	auid_31 = extract_auid_after_marker(data, pos_31, 'building_trader@31')
	print()

# Check building_trader@818
print('2. building_trader@818 (should map to 807991996):')
pos_818 = data.find(b'building_trader@818')
if pos_818 != -1:
	auid_818 = extract_auid_after_marker(data, pos_818, 'building_trader@818')
	print()

# Check a few more building_trader markers to understand the pattern
print('3. Sampling other building_trader markers:')
pattern = b'building_trader@'
pos = 0
samples = []
for i in range(10):
	pos = data.find(pattern, pos)
	if pos == -1:
		break

	# Extract the number
	num_start = pos + len(pattern)
	num_end = num_start
	while num_end < len(data) and data[num_end:num_end+1].isdigit():
		num_end += 1

	if num_end > num_start:
		building_num = data[num_start:num_end].decode('ascii')
		marker_name = f'building_trader@{building_num}'

		auid = extract_auid_after_marker(data, pos, marker_name)
		if auid:
			samples.append((building_num, auid))
		print()

	pos = num_end + 1

print()
print('=' * 80)
print('SUMMARY')
print('=' * 80)
print()

if samples:
	print('Building Number -> auid mapping:')
	for building_num, auid in samples[:15]:
		print(f'  building_trader@{building_num} -> auid {auid}')
	print()

	# Check if any auid matches our target
	target_id = 807991996
	matching = [num for num, auid in samples if auid == target_id]
	if matching:
		print(f'✓ Found auid {target_id} for: {matching}')
	else:
		print(f'✗ No auid matches {target_id}')
