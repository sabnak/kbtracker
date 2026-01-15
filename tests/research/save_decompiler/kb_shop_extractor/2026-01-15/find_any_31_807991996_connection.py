#!/usr/bin/env python3
"""Search for ANY connection between 31 and 807991996 anywhere in save file"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ANY 31-807991996 CONNECTION')
print('=' * 80)
print()

# Find all occurrences of "31" as text (could be building_trader@31 or just "31")
# Find all occurrences of "807991996" as text

pattern_31 = b'31'
pattern_actor = b'807991996'

positions_31 = []
pos = 0
while True:
	pos = data.find(pattern_31, pos)
	if pos == -1:
		break
	positions_31.append(pos)
	pos += 1

positions_actor = []
pos = 0
while True:
	pos = data.find(pattern_actor, pos)
	if pos == -1:
		break
	positions_actor.append(pos)
	pos += 1

print(f'Found {len(positions_31)} occurrences of "31" (as text)')
print(f'Found {len(positions_actor)} occurrences of "807991996" (as text)')
print()

# Check distances between each occurrence
print('Checking distances between "31" and "807991996":')
print('-' * 80)
print()

for actor_pos in positions_actor:
	print(f'Actor 807991996 at position {actor_pos}:')

	# Find closest "31" before and after
	before_31 = [p for p in positions_31 if p < actor_pos]
	after_31 = [p for p in positions_31 if p > actor_pos]

	if before_31:
		closest_before = before_31[-1]
		distance = actor_pos - closest_before
		print(f'  Closest "31" BEFORE: position {closest_before} (distance: {distance} bytes)')

		if distance < 5000:
			# Show what's between them
			chunk = data[closest_before:actor_pos + 10]
			print(f'  Text between: {chunk.decode("ascii", errors="ignore")[:200]}')

	if after_31:
		closest_after = after_31[0]
		distance = closest_after - actor_pos
		print(f'  Closest "31" AFTER: position {closest_after} (distance: {distance} bytes)')

		if distance < 5000:
			# Show what's between them
			chunk = data[actor_pos:closest_after + 10]
			print(f'  Text between: {chunk.decode("ascii", errors="ignore")[:200]}')

	print()

print('=' * 80)
print()

# Look for other table-like structures
print('Looking for other table/mapping structures:')
print('-' * 80)
print()

# Search for patterns like "XX -> YYYYYYYY" where XX could be building numbers
# and YYYYYYYY could be actor IDs

# Try to find regions with repetitive structure
print('Searching for repetitive patterns with large integers...')
print()

# Sample different areas of the file
sample_positions = [
	(0, 100000, 'Start of file'),
	(1000000, 1100000, 'Around 1MB'),
	(2000000, 2200000, 'Around 2MB (lookup table area)'),
	(5000000, 5100000, 'Around 5MB'),
	(8000000, 8100000, 'Around 8MB'),
	(len(data) - 100000, len(data), 'End of file')
]

for start, end, label in sample_positions:
	if end > len(data):
		continue

	chunk = data[start:end]

	# Count how many 8-9 digit numbers appear
	pattern = rb'\b\d{8,9}\b'
	matches = list(re.finditer(pattern, chunk))

	if len(matches) > 20:
		print(f'{label} ({start}-{end}): {len(matches)} large numbers')

		# Show sample
		for match in matches[:5]:
			pos = start + match.start()
			number = match.group(0).decode('ascii')

			# Show context
			ctx_start = match.start() - 50
			ctx_end = match.end() + 50
			ctx = chunk[max(0, ctx_start):min(len(chunk), ctx_end)]

			print(f'  {pos}: {number}')
			print(f'    Context: {ctx.decode("ascii", errors="ignore")[:100]}')
		print()

print('=' * 80)
