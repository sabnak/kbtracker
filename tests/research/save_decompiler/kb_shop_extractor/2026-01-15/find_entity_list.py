#!/usr/bin/env python3
"""Search for a global entity list that might map buildings to actors"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR GLOBAL ENTITY/SPAWN LIST')
print('=' * 80)
print()

# Known facts:
# - building_trader@31 at position 669916 has bocman
# - actor_807991996 belongs to this shop (according to user)
# - This actor ID appears in lookup table with building_trader@818

# Strategy: Look for sections that might list all spawned entities
# These sections might have pairs of (building_num, actor_id) or (position, actor_id)

# Look for the auid value of building_trader@31
building_31_auid = 50331649  # We found this earlier

print(f'building_trader@31 auid: {building_31_auid}')
print()

# Search for this auid value in the save
auid_bytes = struct.pack('<I', building_31_auid)
pos = 0
occurrences = []

while True:
	pos = data.find(auid_bytes, pos)
	if pos == -1:
		break
	occurrences.append(pos)
	pos += 1

print(f'Found auid {building_31_auid} at {len(occurrences)} positions:')
for p in occurrences[:10]:
	print(f'  Position {p}')

print()

# For each occurrence, check if actor_807991996 is nearby
print('Checking if actor_807991996 appears near any auid occurrence:')
print('-' * 80)

actor_id = 807991996
found_connection = False

for auid_pos in occurrences:
	# Search 1000 bytes before and after
	search_start = max(0, auid_pos - 1000)
	search_end = min(len(data), auid_pos + 1000)

	# Check as ASCII
	chunk = data[search_start:search_end]
	if b'807991996' in chunk:
		offset = chunk.find(b'807991996') + search_start - auid_pos
		print(f'✓ Found at auid position {auid_pos}, actor at offset {offset:+d}')
		found_connection = True

		# Show context
		context_start = max(0, auid_pos - 100)
		context_end = min(len(data), auid_pos + 100)
		context = data[context_start:context_end]
		print(f'  Context: {context.decode("ascii", errors="ignore")[:200]}')

if not found_connection:
	print('No connection found between auid and actor_807991996')

print()
print('=' * 80)
