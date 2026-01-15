#!/usr/bin/env python3
"""Search for alternative mapping structure for building_trader@31"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('SEARCHING FOR ALTERNATIVE MAPPING FOR building_trader@31')
print('=' * 80)
print()

# We know:
# - building_trader@31 is NOT in the actor mapping section (se ... actor_id)
# - building_trader@31 IS in a reference list section
# - actor_807991996 is in the mapping section with building_trader@818

# Maybe the reference list is an INDEX into the actor mapping section?
# Let's extract both lists and see if there's a correlation

lookup_start = 2160000
lookup_end = 2180000
chunk = data[lookup_start:lookup_end]
text = chunk.decode('ascii', errors='ignore')

# Extract actor mapping section (building_trader@ with "se" and actor IDs)
print('1. ACTOR MAPPING SECTION (building_trader@ with actor IDs):')
print('-' * 80)

mapping_pattern = r'building_trader@(\d+).{1,50}se\D+(\d{8,9})'
mapping_matches = list(re.finditer(mapping_pattern, text))

actor_mappings = []
for match in mapping_matches:
	building_num = int(match.group(1))
	actor_id = int(match.group(2))
	actor_mappings.append((building_num, actor_id))

actor_mappings.sort(key=lambda x: x[0])

print(f'Found {len(actor_mappings)} mappings')
for building_num, actor_id in actor_mappings[:20]:
	marker = "★" if actor_id == 807991996 else " "
	print(f'{marker} building_trader@{building_num:4d} -> actor_{actor_id}')

print()
print('=' * 80)
print()

# Extract reference list section (building_trader@ followed by "lu")
print('2. REFERENCE LIST SECTION (building_trader@ in list):')
print('-' * 80)

# Find the section with building_trader@31
ref_section_start = text.find('building_trader@1332')
if ref_section_start != -1:
	ref_section = text[ref_section_start:ref_section_start+500]
	print('Section containing building_trader@31:')
	print(ref_section[:400])
	print()

	# Extract all building_trader numbers from this section
	ref_pattern = r'building_trader@(\d+)'
	ref_matches = list(re.finditer(ref_pattern, ref_section))

	ref_list = []
	for match in ref_matches:
		building_num = int(match.group(1))
		ref_list.append(building_num)

	print(f'Building traders in reference list: {ref_list[:20]}')
	print()

	# Check if position in this list corresponds to position in actor mapping list
	print('Testing if reference list is an INDEX into actor mapping list:')
	print('-' * 40)

	if 31 in ref_list:
		idx_of_31 = ref_list.index(31)
		print(f'building_trader@31 is at index {idx_of_31} in reference list')

		if idx_of_31 < len(actor_mappings):
			mapped_building, mapped_actor = actor_mappings[idx_of_31]
			print(f'Actor mapping at index {idx_of_31}: building_trader@{mapped_building} -> actor_{mapped_actor}')

			if mapped_actor == 807991996:
				print(f'  ✓✓✓ MATCH! Index {idx_of_31} points to actor_807991996!')
		print()

print('=' * 80)
