#!/usr/bin/env python3
"""Search for entity/spawn lists that might contain actor-building_trader bindings"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ENTITY/SPAWN LISTS IN SAVE FILE')
print('=' * 80)
print()

# Strategy: Look for sections with repeating structures that might contain:
# - Actor IDs (9-digit numbers)
# - Building_trader numbers (small numbers)
# - Coordinates or other identifying data

# All dragondor actors from .act files:
dragondor_actors = [110905037, 1167461685, 1815772648, 608572288, 807991996, 886465971]

print('Dragondor actors (from .act files):')
for actor_id in dragondor_actors:
	print(f'  actor_{actor_id}')
print()

# Search for these actor IDs as binary integers in the save
print('=' * 80)
print('SEARCHING FOR DRAGONDOR ACTOR IDs IN SAVE FILE:')
print('=' * 80)
print()

actor_positions = {}

for actor_id in dragondor_actors:
	le_bytes = struct.pack('<I', actor_id)
	positions = []

	pos = 0
	while True:
		pos = data.find(le_bytes, pos)
		if pos == -1:
			break
		positions.append(pos)
		pos += 1

	if positions:
		actor_positions[actor_id] = positions
		print(f'actor_{actor_id}: found at {len(positions)} position(s)')
		for p in positions[:3]:
			print(f'  Position {p}')
	else:
		print(f'actor_{actor_id}: NOT FOUND')

print()
print('=' * 80)
print()

# If actor_807991996 is found, examine the structure around it
if 807991996 in actor_positions:
	print('EXAMINING STRUCTURE AROUND actor_807991996:')
	print('-' * 80)
	print()

	for pos in actor_positions[807991996]:
		print(f'Position {pos}:')

		# Show 200 bytes before and after
		start = max(0, pos - 200)
		end = min(len(data), pos + 200)
		chunk = data[start:end]

		print('ASCII context:')
		print(chunk.decode('ascii', errors='ignore'))
		print()

		# Look for small integers before the actor ID (could be building_trader number)
		print('Checking for small integers (0-2000) within 50 bytes before:')
		scan_start = max(0, pos - 50)
		scan_chunk = data[scan_start:pos]

		for offset in range(0, len(scan_chunk) - 4, 4):
			value = struct.unpack('<I', scan_chunk[offset:offset+4])[0]
			if 0 < value < 2000:
				abs_pos = scan_start + offset
				distance = pos - abs_pos
				print(f'  Position {abs_pos} (offset -{distance}): value={value}')

				# Check if this could be a building_trader number
				# Does building_trader@{value} exist in dragondor?
				bt_pattern = f'building_trader@{value}'.encode('ascii')
				if bt_pattern in data:
					# Check if it's in dragondor
					bt_pos = data.find(bt_pattern)
					search_before = data[max(0, bt_pos - 500):bt_pos]
					if b'dragondor' in search_before:
						print(f'    ✓✓✓ building_trader@{value} EXISTS in dragondor!')

		print()
		print('-' * 80)
		print()

else:
	print('actor_807991996 NOT FOUND in save file as binary integer')

print()
print('=' * 80)
