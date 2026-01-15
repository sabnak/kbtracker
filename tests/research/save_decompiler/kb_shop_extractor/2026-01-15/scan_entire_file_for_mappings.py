#!/usr/bin/env python3
"""Scan ENTIRE save file for any structure that might map building_trader to actors"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SCANNING ENTIRE FILE FOR building_trader/actor MAPPING STRUCTURES')
print('=' * 80)
print()

# Strategy: Find regions with repeated patterns that might be entity lists

# 1. Look for sections with many "building_trader@" references
print('1. Sections with high density of "building_trader@":')
print('-' * 80)

chunk_size = 50000
high_density = []

for start in range(0, len(data), chunk_size):
	end = min(start + chunk_size, len(data))
	chunk = data[start:end]

	count = chunk.count(b'building_trader@')

	if count > 20:
		high_density.append((start, end, count))

print(f'Found {len(high_density)} high-density regions')
for start, end, count in high_density:
	print(f'  Position {start}-{end}: {count} occurrences')

	#
	# Check if building_trader@31 is in this region
	if b'building_trader@31' in data[start:end]:
		print(f'    ★ Contains building_trader@31')

print()
print('=' * 80)
print()

# 2. Look for sections that might contain spawn/placement data
# These might have coordinates + entity IDs
print('2. Searching for patterns like: building_trader@X followed by numbers:')
print('-' * 80)

# Find all building_trader@31 occurrences
pattern = rb'building_trader@31(?!\d)'
matches = list(re.finditer(pattern, data))

print(f'Found {len(matches)} occurrences of building_trader@31')
print()

for i, match in enumerate(matches, 1):
	pos = match.start()
	print(f'{i}. Position {pos}:')

	# Show 300 bytes after
	chunk = data[pos:pos+300]

	# Check for any large numbers that could be actor IDs
	text = chunk.decode('ascii', errors='ignore')
	large_nums = re.findall(r'\b(\d{8,9})\b', text)

	if large_nums:
		print(f'   Large numbers nearby: {large_nums[:5]}')

	# Check if "807991996" appears anywhere in the next 5000 bytes
	extended = data[pos:pos+5000]
	if b'807991996' in extended:
		offset = extended.find(b'807991996')
		print(f'   ★★★ FOUND 807991996 at offset +{offset}!')

		# Show context
		context_start = max(0, offset - 100)
		context_end = min(len(extended), offset + 100)
		context = extended[context_start:context_end].decode('ascii', errors='ignore')
		print(f'   Context: {context[:200]}')

	print()

print('=' * 80)
