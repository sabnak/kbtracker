#!/usr/bin/env python3
"""Parse all actor files to build actor_id -> location mapping"""

from pathlib import Path
import struct

actor_dir = Path('z:/1/kb/darkside/ses')

print('=' * 80)
print('PARSING ALL ACTOR FILES')
print('=' * 80)
print()

# Parse all .act files
actors_by_location = {}

for actor_file in actor_dir.glob('*.act'):
	try:
		with open(actor_file, 'rb') as f:
			data = f.read()

		# Extract actor ID from filename
		actor_id = actor_file.stem

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

			if location not in actors_by_location:
				actors_by_location[location] = []

			actors_by_location[location].append(actor_id)

	except Exception as e:
		print(f'Error parsing {actor_file}: {e}')

print(f'Total locations: {len(actors_by_location)}')
print()

# Show dragondor actors
print('Actors in dragondor:')
print('-' * 80)
if 'dragondor' in actors_by_location:
	dragondor_actors = sorted(actors_by_location['dragondor'])
	print(f'Count: {len(dragondor_actors)}')
	print()
	for actor_id in dragondor_actors:
		print(f'  actor_{actor_id}')
else:
	print('  No actors found in dragondor!')

print()
print('=' * 80)
print()

# Show m_inselburg actors
print('Actors in m_inselburg:')
print('-' * 80)
if 'm_inselburg' in actors_by_location:
	inselburg_actors = sorted(actors_by_location['m_inselburg'])
	print(f'Count: {len(inselburg_actors)}')
	print()
	for actor_id in inselburg_actors:
		print(f'  actor_{actor_id}')
else:
	print('  No actors found in m_inselburg!')

print()
print('=' * 80)
print()

# Summary
print('SUMMARY:')
print('-' * 80)
print()
print(f'Total actors parsed: {sum(len(v) for v in actors_by_location.values())}')
print(f'Locations with multiple actors:')
for loc in sorted(actors_by_location.keys()):
	count = len(actors_by_location[loc])
	if count > 1:
		print(f'  {loc}: {count} actors')

print()
print('=' * 80)
