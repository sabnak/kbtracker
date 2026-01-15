#!/usr/bin/env python3
"""Analyze when bit 7 is set vs not set in strg values"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('ANALYZING BIT 7 PATTERN IN .actors strg VALUES')
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

bit7_set = []
bit7_not_set = []

for match in matches:
	building_num = match.group(1).decode('ascii')
	building_pos = match.start()

	# Look for .actors section within 3000 bytes before
	search_start = max(0, building_pos - 3000)
	search_chunk = data[search_start:building_pos]

	actors_pos = search_chunk.rfind(b'.actors')
	if actors_pos == -1:
		continue

	abs_actors_pos = search_start + actors_pos
	chunk = data[abs_actors_pos:abs_actors_pos + 100]
	strg_pos = chunk.find(b'strg')

	if strg_pos == -1:
		continue

	value_offset = strg_pos + 8
	if value_offset + 4 > len(chunk):
		continue

	strg_value = struct.unpack('<I', chunk[value_offset:value_offset + 4])[0]
	strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))

	# Check if shop has inventory
	has_inventory = False
	search_inv = data[abs_actors_pos:building_pos]
	if b'.shopunits' in search_inv or b'.spells' in search_inv:
		has_inventory = True

	entry = {
		'building_num': building_num,
		'strg_value': strg_value,
		'actor_id': extract_actor_id_from_strg(strg_value),
		'has_inventory': has_inventory
	}

	if (strg_bytes[3] & 0x80) != 0:
		bit7_set.append(entry)
	else:
		bit7_not_set.append(entry)

print(f'Total shops analyzed: {len(bit7_set) + len(bit7_not_set)}')
print(f'  Bit 7 SET: {len(bit7_set)}')
print(f'  Bit 7 NOT set: {len(bit7_not_set)}')
print()

print('=' * 80)
print('SHOPS WITH BIT 7 NOT SET:')
print('=' * 80)
print()

# Group by strg value
from collections import defaultdict
grouped_no_bit7 = defaultdict(list)
for entry in bit7_not_set:
	grouped_no_bit7[entry['strg_value']].append(entry)

for strg_value, entries in sorted(grouped_no_bit7.items()):
	print(f'strg value: 0x{strg_value:08x} (actor_{entries[0]["actor_id"]})')
	print(f'  Count: {len(entries)} shops')

	# Check if any have inventory
	with_inv = sum(1 for e in entries if e['has_inventory'])
	print(f'  With inventory: {with_inv}/{len(entries)}')

	# Show first few building numbers
	building_nums = [e['building_num'] for e in entries[:5]]
	print(f'  Examples: building_trader@{", @".join(building_nums)}{"..." if len(entries) > 5 else ""}')
	print()

print('=' * 80)
print('SHOPS WITH BIT 7 SET (first 10):')
print('=' * 80)
print()

for entry in bit7_set[:10]:
	inv_status = 'WITH inventory' if entry['has_inventory'] else 'NO inventory'
	print(f'building_trader@{entry["building_num"]:4s}: actor_{entry["actor_id"]:10d} - {inv_status}')

print()
print(f'... and {len(bit7_set) - 10} more')
print()

# Summary stats
bit7_set_with_inv = sum(1 for e in bit7_set if e['has_inventory'])
bit7_not_set_with_inv = sum(1 for e in bit7_not_set if e['has_inventory'])

print('=' * 80)
print('INVENTORY CORRELATION:')
print('=' * 80)
print(f'Bit 7 SET shops:     {bit7_set_with_inv}/{len(bit7_set)} have inventory ({100*bit7_set_with_inv/len(bit7_set):.1f}%)')
print(f'Bit 7 NOT SET shops: {bit7_not_set_with_inv}/{len(bit7_not_set)} have inventory ({100*bit7_not_set_with_inv/len(bit7_not_set):.1f}%)')
print('=' * 80)
