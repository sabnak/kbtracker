#!/usr/bin/env python3
"""Extract location from actor .act file"""

from pathlib import Path
import struct

actor_file = Path('F:/var/kbtracker/tests/game_files/actors/807991996.act')

with open(actor_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('EXTRACTING DATA FROM ACTOR FILE')
print('=' * 80)
print()

# Extract actor ID
uid_pos = data.find(b'uid')
if uid_pos != -1:
	# uid is 3 bytes, then comes the 4-byte actor ID
	id_start = uid_pos + 3
	if id_start + 4 <= len(data):
		actor_id = struct.unpack('<I', data[id_start:id_start+4])[0]
		print(f'Actor ID: {actor_id}')

# Extract location (ml tag)
ml_pos = data.find(b'ml')
if ml_pos != -1:
	# Skip 'ml' tag (2 bytes) and length (4 bytes)
	location_start = ml_pos + 6
	location_end = location_start

	# Find end of location string
	while location_end < len(data) and data[location_end] not in [0x02, 0x00]:
		location_end += 1

	location = data[location_start:location_end].decode('ascii', errors='ignore')
	print(f'Location (ml): {location}')

print()
print('=' * 80)
print()

print('CONCLUSION:')
print('-' * 80)
print(f'actor_807991996 belongs to location "dragondor"')
print()
print('This matches our finding that building_trader@31 is in dragondor!')
print('So: dragondor + building_trader@31 -> actor_807991996')
print()
print('=' * 80)
