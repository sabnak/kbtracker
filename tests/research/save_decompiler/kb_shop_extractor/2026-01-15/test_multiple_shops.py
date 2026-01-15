#!/usr/bin/env python3
"""Test actor extraction on multiple building_trader@ shops"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('TESTING ACTOR ID EXTRACTION ON MULTIPLE SHOPS')
print('=' * 80)
print()

def extract_actor_id_from_strg(strg_value):
	"""Extract actor ID by clearing bit 7 of last byte"""
	strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))
	actor_bytes = list(strg_bytes)
	actor_bytes[3] = actor_bytes[3] & 0x7F  # Clear bit 7
	actor_id = struct.unpack('<I', bytes(actor_bytes))[0]
	return actor_id

# Find all building_trader@ patterns
pattern = rb'building_trader@(\d+)(?!\d)'
matches = list(re.finditer(pattern, data))

print(f'Found {len(matches)} building_trader@ patterns')
print()

# Test the first 10 shops
tested = 0
successful = 0
failed = 0

for match in matches[:15]:
	building_num = match.group(1).decode('ascii')
	building_pos = match.start()

	# Look for .actors section within 3000 bytes before
	search_start = max(0, building_pos - 3000)
	search_chunk = data[search_start:building_pos]

	actors_pos = search_chunk.rfind(b'.actors')

	if actors_pos == -1:
		continue

	tested += 1
	abs_actors_pos = search_start + actors_pos

	# Extract .actors section
	chunk = data[abs_actors_pos:abs_actors_pos + 100]
	strg_pos = chunk.find(b'strg')

	if strg_pos == -1:
		print(f'building_trader@{building_num}: No strg in .actors')
		failed += 1
		continue

	# Extract strg value
	value_offset = strg_pos + 8
	if value_offset + 4 > len(chunk):
		print(f'building_trader@{building_num}: strg value out of bounds')
		failed += 1
		continue

	strg_value = struct.unpack('<I', chunk[value_offset:value_offset + 4])[0]
	actor_id = extract_actor_id_from_strg(strg_value)

	# Extract location
	lt_search_start = max(0, building_pos - 100)
	lt_pos = data.rfind(b'lt', lt_search_start, building_pos)
	location = 'unknown'

	if lt_pos != -1 and lt_pos > building_pos - 50:
		try:
			lt_length = struct.unpack('<I', data[lt_pos + 2:lt_pos + 6])[0]
			if lt_length < 100:
				location = data[lt_pos + 6:lt_pos + 6 + lt_length].decode('utf-16-le', errors='ignore')
		except:
			pass

	# Verify bit 7 pattern
	strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))
	actor_bytes = struct.unpack('4B', struct.pack('<I', actor_id))

	bit7_set = (strg_bytes[3] & 0x80) != 0
	bit7_check = '✓' if bit7_set else '✗'

	print(f'{bit7_check} building_trader@{building_num:4s} ({location:20s}): actor_{actor_id}')
	print(f'   strg: 0x{strg_value:08x}, last_byte: 0x{strg_bytes[3]:02x} (bit7: {bit7_set})')

	if bit7_set:
		successful += 1
	else:
		failed += 1

print()
print('=' * 80)
print(f'SUMMARY: Tested {tested} shops')
print(f'  Successful (bit 7 set): {successful}')
print(f'  Failed (bit 7 not set): {failed}')
print('=' * 80)
