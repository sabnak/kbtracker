#!/usr/bin/env python3
"""Search save file for actor-building_trader binding in different sections"""

from pathlib import Path
import re
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ACTOR-BUILDING_TRADER BINDING IN SAVE FILE')
print('=' * 80)
print()

# We know:
# - building_trader@31 at position 669916 in dragondor
# - actor_807991996 belongs to dragondor (from .act file)

# Strategy: Search for sections that might contain entity lists/spawn data
# Look for patterns like repeated structures with IDs

# 1. Search for "actor_system" strings in save (might be references to actors)
print('1. Searching for "actor_system" strings:')
print('-' * 80)

pattern = rb'actor_system_\d+'
matches = list(re.finditer(pattern, data))
print(f'Found {len(matches)} "actor_system_XXXXXXX" strings')

if matches:
	# Check if any are near our target actor
	for match in matches[:20]:
		text = match.group(0).decode('ascii')
		if '807991996' in text:
			pos = match.start()
			print(f'\n*** FOUND TARGET: {text} at position {pos} ***')

			# Show context
			context = data[max(0, pos-500):pos+500]
			print(f'Context (ASCII):')
			print(context.decode('ascii', errors='ignore')[:500])

print()
print('=' * 80)
print()

# 2. Look for sections with high density of 9-digit numbers (could be actor IDs)
print('2. Searching for regions with many 9-digit actor IDs:')
print('-' * 80)

# Scan file in chunks
chunk_size = 50000
high_density_regions = []

for start in range(0, len(data), chunk_size):
	end = min(start + chunk_size, len(data))
	chunk = data[start:end]

	# Count 9-digit numbers as text
	text = chunk.decode('ascii', errors='ignore')
	pattern = r'\b\d{9}\b'
	matches = list(re.finditer(pattern, text))

	if len(matches) > 10:  # More than 10 per 50KB
		high_density_regions.append((start, end, len(matches)))

print(f'Found {len(high_density_regions)} regions with high density of 9-digit numbers')
for start, end, count in high_density_regions[:10]:
	print(f'  Position {start}-{end}: {count} numbers')

	# Check if this region is near our target
	if any(669000 < pos < 670000 for pos in [start, end]):
		print(f'    *** NEAR building_trader@31! ***')

print()
print('=' * 80)
print()

# 3. Search for binary structures that might link building_trader to actor
print('3. Searching for structures linking @31 to actor_807991996:')
print('-' * 80)

# Look for 31 (as 4-byte int) followed within 100 bytes by 807991996 (as 4-byte int)
target_building = 31
target_actor = 807991996

print(f'Searching for building#{target_building} and actor#{target_actor} stored together...')

found_pairs = []
for pos in range(0, len(data) - 200):
	# Check if we have 31 as little-endian int
	if pos + 4 <= len(data):
		value1 = struct.unpack('<I', data[pos:pos+4])[0]

		if value1 == target_building:
			# Look for actor ID in next 200 bytes
			search_chunk = data[pos:pos+200]
			for offset in range(0, len(search_chunk) - 4):
				value2 = struct.unpack('<I', search_chunk[offset:offset+4])[0]
				if value2 == target_actor:
					found_pairs.append((pos, offset))
					break

if found_pairs:
	print(f'\nFound {len(found_pairs)} potential matches:')
	for base_pos, offset in found_pairs[:5]:
		print(f'  Position {base_pos}: building#{target_building}, actor#{target_actor} at offset +{offset}')

		# Show context
		context = data[base_pos:base_pos+offset+20]
		print(f'  Hex: {context.hex()}')
		print(f'  ASCII: {context.decode("ascii", errors="ignore")}')
		print()
else:
	print('No matches found.')

print()
print('=' * 80)
