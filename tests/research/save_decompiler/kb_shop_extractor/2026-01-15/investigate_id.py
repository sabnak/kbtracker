#!/usr/bin/env python3
"""Comprehensive investigation of ID 807991996 and building_trader@31"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('INVESTIGATING ID 807991996 AND building_trader@31')
print('=' * 80)
print()

# The ID as different binary representations
target_id = 807991996
print(f'Target ID: {target_id}')
print()

# 1. Search for ID as little-endian 32-bit integer
le_bytes = struct.pack('<I', target_id)
print(f'1. Searching for ID as little-endian bytes: {le_bytes.hex()}')
le_positions = []
pos = 0
while True:
	pos = data.find(le_bytes, pos)
	if pos == -1:
		break
	le_positions.append(pos)
	pos += 1

print(f'   Found at {len(le_positions)} positions: {le_positions}')
print()

# 2. Search for ID as big-endian 32-bit integer
be_bytes = struct.pack('>I', target_id)
print(f'2. Searching for ID as big-endian bytes: {be_bytes.hex()}')
be_positions = []
pos = 0
while True:
	pos = data.find(be_bytes, pos)
	if pos == -1:
		break
	be_positions.append(pos)
	pos += 1

print(f'   Found at {len(be_positions)} positions: {be_positions}')
print()

# 3. Find building_trader@31 position
print('3. Locating building_trader@31:')
pattern = b'building_trader@31'
pos = data.find(pattern)
if pos != -1:
	print(f'   Found at position: {pos}')
	building_31_pos = pos

	# Show surrounding context
	print()
	print('   Context (500 bytes before and after):')
	start = max(0, pos - 500)
	end = min(len(data), pos + 500)
	chunk = data[start:end]

	# Try to decode as much as possible
	try:
		text = chunk.decode('utf-16-le', errors='ignore')
		print('   [UTF-16-LE decode]')
		print(text[:500])
	except:
		pass

	print()
	print('   [ASCII decode]')
	text_ascii = chunk.decode('ascii', errors='ignore')
	print(text_ascii[:500])

	# 4. Check if any binary representations are near building_trader@31
	print()
	print('4. Checking for ID representations within 1000 bytes of building_trader@31:')
	search_start = max(0, building_31_pos - 1000)
	search_end = min(len(data), building_31_pos + 1000)

	# Check for little-endian
	if any(search_start <= p < search_end for p in le_positions):
		nearby_le = [p for p in le_positions if search_start <= p < search_end]
		print(f'   ✓ Little-endian found at: {nearby_le} (offset from building_trader@31: {[p - building_31_pos for p in nearby_le]})')
	else:
		print('   ✗ Little-endian NOT found nearby')

	# Check for big-endian
	if any(search_start <= p < search_end for p in be_positions):
		nearby_be = [p for p in be_positions if search_start <= p < search_end]
		print(f'   ✓ Big-endian found at: {nearby_be} (offset from building_trader@31: {[p - building_31_pos for p in nearby_be]})')
	else:
		print('   ✗ Big-endian NOT found nearby')

	print()

	# 5. Look for the bocman inventory near building_trader@31
	print('5. Verifying bocman inventory location:')
	bocman_pattern = b'bocman'
	search_area = data[building_31_pos - 1000:building_31_pos + 500]
	bocman_pos_in_area = search_area.find(bocman_pattern)
	if bocman_pos_in_area != -1:
		abs_bocman_pos = building_31_pos - 1000 + bocman_pos_in_area
		print(f'   Found bocman at: {abs_bocman_pos} (offset from building_trader@31: {abs_bocman_pos - building_31_pos})')
	else:
		print('   Bocman not found in nearby area')
else:
	print('   building_trader@31 NOT FOUND!')

print()
print('=' * 80)
print()

# 6. Check the lookup table entry for building_trader@818
print('6. Examining building_trader@818 (which DOES have ID 807991996 in lookup table):')
pattern_818 = b'building_trader@818'
pos_818 = data.find(pattern_818)
if pos_818 != -1:
	print(f'   Found at position: {pos_818}')

	# Show context
	start = max(0, pos_818 - 200)
	end = min(len(data), pos_818 + 200)
	chunk = data[start:end]
	text = chunk.decode('ascii', errors='ignore')
	print(f'   Context: {text}')

	# Check for binary ID nearby
	search_start = max(0, pos_818 - 1000)
	search_end = min(len(data), pos_818 + 1000)

	if any(search_start <= p < search_end for p in le_positions):
		nearby_le = [p for p in le_positions if search_start <= p < search_end]
		print(f'   Little-endian ID found at: {nearby_le} (offset from building_trader@818: {[p - pos_818 for p in nearby_le]})')
else:
	print('   building_trader@818 NOT FOUND!')

print()
print('=' * 80)
