#!/usr/bin/env python3
"""Investigate building_trader@818 structure"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('INVESTIGATING building_trader@818')
print('=' * 80)
print()

# Find building_trader@818
pattern = rb'building_trader@818(?!\d)'
match = re.search(pattern, data)

if not match:
	print('building_trader@818 not found!')
else:
	pos_818 = match.start()
	print(f'building_trader@818 found at position {pos_818}')
	print()

	# Check for location tag before it
	lt_search_start = max(0, pos_818 - 100)
	lt_pos = data.rfind(b'lt', lt_search_start, pos_818)

	if lt_pos != -1:
		lt_length = struct.unpack('<I', data[lt_pos + 2:lt_pos + 6])[0]
		location = data[lt_pos + 6:lt_pos + 6 + lt_length].decode('utf-16-le', errors='ignore')
		print(f'Location: {location}')
	print()

	# Check for inventory sections BEFORE building_trader@818
	print('Checking for inventory sections BEFORE building_trader@818:')
	print('-' * 60)

	search_start = max(0, pos_818 - 3000)
	search_chunk = data[search_start:pos_818]

	sections = ['.shopunits', '.spells', '.items', '.garrison', '.actors', '.temp']
	found_sections = []

	for section in sections:
		section_bytes = section.encode('ascii')
		section_pos = search_chunk.rfind(section_bytes)
		if section_pos != -1:
			abs_pos = search_start + section_pos
			offset = abs_pos - pos_818
			found_sections.append((section, abs_pos, offset))
			print(f'  {section:15s} at position {abs_pos} (offset {offset:+d})')

	if not found_sections:
		print('  No inventory sections found')

	print()

	# Check for inventory sections AFTER building_trader@818
	print('Checking for inventory sections AFTER building_trader@818:')
	print('-' * 60)

	search_end = min(len(data), pos_818 + 3000)
	search_chunk_after = data[pos_818:search_end]

	found_after = []
	for section in sections:
		section_bytes = section.encode('ascii')
		section_pos = search_chunk_after.find(section_bytes)
		if section_pos != -1:
			abs_pos = pos_818 + section_pos
			offset = abs_pos - pos_818
			found_after.append((section, abs_pos, offset))
			print(f'  {section:15s} at position {abs_pos} (offset {offset:+d})')

	if not found_after:
		print('  No inventory sections found')

	print()
	print('=' * 80)
	print()

	# Show context around building_trader@818
	print('CONTEXT AROUND building_trader@818:')
	print('-' * 80)

	context_start = max(0, pos_818 - 200)
	context_end = min(len(data), pos_818 + 200)
	context = data[context_start:context_end]

	print('ASCII:')
	print(context.decode('ascii', errors='ignore'))
	print()

	print('=' * 80)
