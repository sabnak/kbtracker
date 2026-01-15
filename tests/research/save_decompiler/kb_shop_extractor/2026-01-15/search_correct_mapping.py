#!/usr/bin/env python3
"""Search for correct actor-trader mapping structure"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR CORRECT ACTOR-TRADER MAPPING')
print('=' * 80)
print()

# Known facts:
# - building_trader@31 in dragondor should map to actor_807991996
# - building_trader@818 in m_inselburg has wrong actor_807991996 in lookup table

# Strategy: Search for the number 31 near actor_807991996
# If the correct mapping exists, maybe 31 and 807991996 are stored near each other

print('1. Searching for number 31 stored as integer near building_trader markers:')
print('-' * 80)
print()

# Find all building_trader@ markers and check what integers are stored nearby
pattern = rb'building_trader@(\d+)'
matches = list(re.finditer(pattern, data))

print(f'Total building_trader@ markers found: {len(matches)}')
print()

# For each one, extract integers stored in the next 200 bytes
print('Sample of integers stored after building_trader@ markers:')
print()

for match in matches[:20]:
	building_num = match.group(1).decode('ascii')
	pos = match.end()

	# Read next 200 bytes and extract all 4-byte integers
	chunk = data[pos:pos + 200]

	integers = []
	for offset in range(0, min(len(chunk) - 4, 50), 4):
		value = struct.unpack('<I', chunk[offset:offset + 4])[0]
		if value < 10000000000:  # Reasonable range
			integers.append((offset, value))

	if integers:
		print(f'building_trader@{building_num} (position {match.start()}):')
		# Show first 10 integers
		for offset, value in integers[:10]:
			if value > 10000000:  # Large numbers (could be actor IDs)
				print(f'  +{offset}: {value} (LARGE - could be actor ID)')
			elif value < 10000:  # Small numbers (could be building_trader numbers)
				print(f'  +{offset}: {value} (small)')
		print()

print()
print('=' * 80)
print()

# Search specifically around building_trader@31
print('2. Detailed analysis of building_trader@31 area:')
print('-' * 80)
print()

pos_31 = data.find(b'building_trader@31\x00')
if pos_31 == -1:
	pos_31 = data.find(b'building_trader@31')

if pos_31 != -1:
	print(f'building_trader@31 found at position {pos_31}')
	print()

	# Extract all 4-byte integers in next 500 bytes
	chunk = data[pos_31:pos_31 + 500]

	print('All 4-byte integers after building_trader@31:')
	for offset in range(0, min(len(chunk) - 4, 200), 1):
		value = struct.unpack('<I', chunk[offset:offset + 4])[0]

		# Check if this could be actor_807991996 or related
		if value == 807991996:
			print(f'  ✓✓✓ +{offset}: {value} - THIS IS ACTOR_807991996!')
		elif value == 31:
			print(f'  +{offset}: {value} - matches building_trader number')
		elif 800000000 <= value <= 810000000:
			print(f'  +{offset}: {value} - in range of target actor ID')

print()
print('=' * 80)
print()

# Search for any area with both 31 and 807991996 nearby
print('3. Searching entire file for 31 and 807991996 stored as integers nearby:')
print('-' * 80)
print()

target_actor = 807991996
target_building = 31

# Scan entire file for both values within 100 bytes
print('Scanning...')
matches_found = 0

for pos in range(0, len(data) - 100):
	chunk = data[pos:pos + 100]

	# Check if both values exist as little-endian integers in this chunk
	has_31 = False
	has_actor = False
	pos_31 = None
	pos_actor = None

	for offset in range(0, len(chunk) - 4):
		value = struct.unpack('<I', chunk[offset:offset + 4])[0]
		if value == 31:
			has_31 = True
			pos_31 = offset
		if value == target_actor:
			has_actor = True
			pos_actor = offset

	if has_31 and has_actor:
		matches_found += 1
		print(f'\n✓ MATCH at position {pos}:')
		print(f'  31 at offset {pos_31}')
		print(f'  807991996 at offset {pos_actor}')
		print(f'  Distance: {abs(pos_actor - pos_31)} bytes')

		# Show ASCII context
		context_start = max(0, pos - 50)
		context_end = min(len(data), pos + 150)
		context = data[context_start:context_end]
		print(f'  Context: {context.decode("ascii", errors="ignore")[:150]}')

		if matches_found >= 5:
			break

if matches_found == 0:
	print('No locations found with both 31 and 807991996 as integers within 100 bytes')

print()
print('=' * 80)
