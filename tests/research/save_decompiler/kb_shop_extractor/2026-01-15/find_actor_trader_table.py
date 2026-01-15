#!/usr/bin/env python3
"""Search for actor-trader mapping table in the save file"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ACTOR-TRADER MAPPING TABLE')
print('=' * 80)
print()

target_actor_id = 807991996

# Convert to different binary formats
le_bytes = struct.pack('<I', target_actor_id)
be_bytes = struct.pack('>I', target_actor_id)

print(f'Target actor ID: {target_actor_id}')
print(f'Little-endian bytes: {le_bytes.hex()}')
print(f'Big-endian bytes: {be_bytes.hex()}')
print()

# Search for the actor ID as binary
print('1. Searching for actor ID as binary (little-endian):')
print('-' * 80)

le_positions = []
pos = 0
while True:
	pos = data.find(le_bytes, pos)
	if pos == -1:
		break
	le_positions.append(pos)
	pos += 1

print(f'Found {len(le_positions)} occurrences')

for i, pos in enumerate(le_positions[:10], 1):
	print(f'\n{i}. Position {pos}:')

	# Show context before and after
	context_start = max(0, pos - 100)
	context_end = min(len(data), pos + 100)
	context = data[context_start:context_end]

	print(f'   Hex: {context.hex()[:200]}...')
	print(f'   ASCII: {context.decode("ascii", errors="ignore")[:150]}')

	# Look for building_trader@ nearby
	search_area = data[max(0, pos - 500):min(len(data), pos + 500)]
	if b'building_trader@' in search_area:
		matches = re.findall(rb'building_trader@(\d+)', search_area)
		if matches:
			print(f'   → Nearby building_trader@: {[m.decode() for m in matches]}')

	# Look for patterns like "31" or numbers that could be building_trader numbers
	# Check for 4-byte integers before and after
	if pos >= 4:
		value_before = struct.unpack('<I', data[pos-4:pos])[0]
		if value_before < 10000:  # Could be a building_trader number
			print(f'   → 4-byte int BEFORE: {value_before}')

	if pos + 8 <= len(data):
		value_after = struct.unpack('<I', data[pos+4:pos+8])[0]
		if value_after < 10000:  # Could be a building_trader number
			print(f'   → 4-byte int AFTER: {value_after}')

print()
print('=' * 80)
print()

# Also search for the number 31 (building_trader@31) as a 4-byte integer near actor IDs
print('2. Looking for areas with multiple actor IDs (potential mapping tables):')
print('-' * 80)

# Check if there's a region with high density of 8-9 digit numbers
print('\nScanning for regions with high concentration of large integers...')

chunk_size = 10000
for chunk_start in range(0, len(data), chunk_size):
	chunk_end = min(chunk_start + chunk_size, len(data))
	chunk = data[chunk_start:chunk_end]

	# Count 8-9 digit integers in this chunk
	count = 0
	for offset in range(0, len(chunk) - 4, 4):
		value = struct.unpack('<I', chunk[offset:offset+4])[0]
		if 10000000 <= value <= 999999999:  # 8-9 digit numbers
			count += 1

	# If high density, report it
	if count > 100:  # More than 100 large integers in 10KB
		print(f'\n  High density region at {chunk_start}-{chunk_end}: {count} large integers')

		# Show sample
		print(f'  Sample integers:')
		sample_count = 0
		for offset in range(0, min(1000, len(chunk) - 4), 4):
			value = struct.unpack('<I', chunk[offset:offset+4])[0]
			if 10000000 <= value <= 999999999:
				print(f'    Position {chunk_start + offset}: {value}')
				sample_count += 1
				if sample_count >= 10:
					break

print()
print('=' * 80)
print()

# Search for "actor_system" or "actor_" strings that might indicate a mapping section
print('3. Searching for "actor_system" or "actor_" strings:')
print('-' * 80)

actor_pattern = rb'actor_system_\d+'
matches = list(re.finditer(actor_pattern, data))
print(f'\nFound {len(matches)} "actor_system_XXXXXXXX" strings')

if matches:
	print('\nFirst 10 occurrences:')
	for i, match in enumerate(matches[:10], 1):
		pos = match.start()
		text = match.group(0).decode('ascii')
		print(f'  {i}. Position {pos}: {text}')

		# Check if our target ID is nearby
		if target_actor_id == int(re.search(r'\d+', text).group()):
			print(f'     *** THIS IS OUR TARGET ACTOR! ***')

print()
print('=' * 80)
