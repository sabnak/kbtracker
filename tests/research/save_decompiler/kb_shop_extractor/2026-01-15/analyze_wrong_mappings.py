#!/usr/bin/env python3
"""Analyze the wrong lookup table to find a pattern"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('ANALYZING WRONG LOOKUP TABLE PATTERN')
print('=' * 80)
print()

# Extract all mappings from the lookup table
lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

# Extract building_trader@XX -> actor_ID mappings
pattern = r'building_trader@(\d+).{1,50}se\D+(\d+)'
matches = list(re.finditer(pattern, text))

print(f'Found {len(matches)} mappings in lookup table:')
print()

mappings = []
for match in matches:
	building_num = int(match.group(1))
	actor_id = int(match.group(2))
	mappings.append((building_num, actor_id))

# Sort by building_trader number
mappings.sort(key=lambda x: x[0])

print('First 30 mappings (sorted by building_trader number):')
print('-' * 80)
print()

for building_num, actor_id in mappings[:30]:
	print(f'building_trader@{building_num:4d} -> actor_{actor_id}')

print()
print('=' * 80)
print()

# Known wrong mappings from user:
# building_trader@818 -> actor_807991996 (WRONG, should be for @31)
# building_trader@893 -> actor_1049716918 (WRONG, from different location)

# Check if 31 appears in the list
has_31 = any(num == 31 for num, _ in mappings)
print(f'Does building_trader@31 appear in lookup table? {has_31}')
print()

# Check what building_trader@818 maps to
mapping_818 = next((actor for num, actor in mappings if num == 818), None)
print(f'building_trader@818 maps to: {mapping_818}')
print()

# Check what building_trader@893 maps to
mapping_893 = next((actor for num, actor in mappings if num == 893), None)
print(f'building_trader@893 maps to: {mapping_893}')
print()

# Check if there's any pattern
# Maybe the mappings are offset? Like building_trader@X actually maps to actor for building_trader@(X+offset)?
print('=' * 80)
print('CHECKING FOR OFFSET PATTERN:')
print('=' * 80)
print()

# User says:
# - actor_807991996 should be for building_trader@31 (but table says it's for @818)
# - Difference: 818 - 31 = 787

print('Known correct mapping: building_trader@31 -> actor_807991996')
print('Lookup table says: building_trader@818 -> actor_807991996')
print(f'Difference: 818 - 31 = 787')
print()

# Check if other mappings are also offset by 787
print('Hypothesis: Maybe all mappings are offset by ~787?')
print('Testing: Does building_trader@(X-787) -> actor_Y mean actor_Y belongs to building_trader@X?')
print()

# Find building_traders around 31+787=818 and 893-787=106
test_nums = [106, 818, 893]
for test_num in test_nums:
	actual_mapping = next((actor for num, actor in mappings if num == test_num), None)
	if actual_mapping:
		hypothetical_correct = test_num - 787
		print(f'building_trader@{test_num} maps to actor_{actual_mapping}')
		print(f'  → Hypothesis: actor_{actual_mapping} might belong to building_trader@{hypothetical_correct}')
		print()

print('=' * 80)
