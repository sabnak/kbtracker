#!/usr/bin/env python3
"""Detailed analysis of the trader name lookup table structure"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('ANALYZING TRADER NAME LOOKUP TABLE')
print('=' * 80)
print()

# Focus on the lookup table area
lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

print('1. Finding all building_trader@ entries in the lookup table:')
print('-' * 80)

# Find ALL building_trader@ mentions
pattern = rb'building_trader@(\d+)'
matches = list(re.finditer(pattern, chunk))

print(f'Found {len(matches)} building_trader@ entries')
print()

# Extract and show context for each match
print('First 20 entries with their context:')
print()

for i, match in enumerate(matches[:20]):
	building_num = match.group(1).decode('ascii')
	pos_in_chunk = match.start()
	abs_pos = lookup_start + pos_in_chunk

	# Show 100 bytes of context after the match
	context_end = min(len(chunk), pos_in_chunk + 100)
	context = chunk[pos_in_chunk:context_end]
	context_ascii = context.decode('ascii', errors='ignore')

	print(f'{i+1}. building_trader@{building_num} at position {abs_pos}')
	print(f'   Context: {context_ascii[:150]}')

	# Try to extract the ID using the pattern
	# Look for 'se' followed by numbers
	se_match = re.search(rb'se.{0,20}(\d{6,})', context)
	if se_match:
		id_value = se_match.group(1).decode('ascii')
		print(f'   → Extracted ID: {id_value}')
	else:
		print(f'   → No ID found with pattern')

	print()

print()
print('=' * 80)
print()

# Specifically look for building_trader@31 and building_trader@818
print('2. Specific lookups:')
print('-' * 80)

for num in ['31', '818']:
	pattern_specific = f'building_trader@{num}'.encode('ascii')
	pos = chunk.find(pattern_specific)

	if pos != -1:
		abs_pos = lookup_start + pos
		context = chunk[pos:pos+150]
		context_ascii = context.decode('ascii', errors='ignore')

		print(f'building_trader@{num}:')
		print(f'  Position: {abs_pos}')
		print(f'  Context: {context_ascii}')

		# Look for any 8-9 digit numbers in context
		numbers = re.findall(rb'\b(\d{8,9})\b', chunk[pos:pos+200])
		if numbers:
			print(f'  8-9 digit numbers nearby: {[n.decode("ascii") for n in numbers]}')
		else:
			print(f'  No 8-9 digit numbers found nearby')
		print()
	else:
		print(f'building_trader@{num}: NOT FOUND in lookup table')
		print()

print('=' * 80)
