#!/usr/bin/env python3
"""Search for actor ID 807991996 stored in different formats near building_trader@31"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ACTOR ID STORAGE NEAR building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916
target_actor_id = 807991996

print(f'building_trader@31 position: {building_31_pos}')
print(f'Target actor ID: {target_actor_id}')
print()

# Search in a large area around the marker
search_start = max(0, building_31_pos - 2000)
search_end = min(len(data), building_31_pos + 1000)
chunk = data[search_start:search_end]

print(f'Searching from position {search_start} to {search_end}')
print('=' * 80)
print()

# Extract ALL 4-byte integers in this area and check if any match
print('Scanning all 4-byte integer values in the area:')
print()

matches_found = []

for offset in range(0, len(chunk) - 4):
	abs_pos = search_start + offset

	# Try little-endian
	value_le = struct.unpack('<I', chunk[offset:offset+4])[0]
	if value_le == target_actor_id:
		distance = abs_pos - building_31_pos
		matches_found.append(('little-endian', abs_pos, distance, offset))
		print(f'✓ MATCH (little-endian): position {abs_pos} (offset {distance:+d} from building_trader@31)')

		# Show context
		context_start = max(0, offset - 50)
		context_end = min(len(chunk), offset + 50)
		context = chunk[context_start:context_end]
		print(f'  Hex context: {context.hex()}')
		print(f'  ASCII context: {context.decode("ascii", errors="ignore")}')
		print()

	# Try big-endian
	value_be = struct.unpack('>I', chunk[offset:offset+4])[0]
	if value_be == target_actor_id:
		distance = abs_pos - building_31_pos
		matches_found.append(('big-endian', abs_pos, distance, offset))
		print(f'✓ MATCH (big-endian): position {abs_pos} (offset {distance:+d} from building_trader@31)')

		# Show context
		context_start = max(0, offset - 50)
		context_end = min(len(chunk), offset + 50)
		context = chunk[context_start:context_end]
		print(f'  Hex context: {context.hex()}')
		print(f'  ASCII context: {context.decode("ascii", errors="ignore")}')
		print()

print('=' * 80)
print()

if not matches_found:
	print('❌ NO MATCHES FOUND')
	print()
	print('Actor ID 807991996 is NOT stored as a 4-byte integer anywhere near building_trader@31')
	print()
	print('Possible explanations:')
	print('1. Actor ID is stored in a different format (not 4-byte integer)')
	print('2. Actor ID is stored in a different location (not near building_trader@ marker)')
	print('3. Actor ID is not stored in the save file at all, must be matched by other means')
else:
	print(f'✓ FOUND {len(matches_found)} MATCH(ES)')
	for encoding, pos, distance, offset in matches_found:
		print(f'  - {encoding} at position {pos} (offset {distance:+d})')

print()
print('=' * 80)
