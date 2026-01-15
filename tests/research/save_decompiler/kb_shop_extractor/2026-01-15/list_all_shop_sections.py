#!/usr/bin/env python3
"""List ALL sections for building_trader@31 shop"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('ALL SECTIONS FOR building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916

# Find start of shop data (look for earliest inventory section)
search_start = max(0, building_31_pos - 3000)
chunk = data[search_start:building_31_pos + 500]

# Find all section markers (sections start with dot)
# Common patterns: .shopunits, .spells, .items, .garrison, .temp, .actors, etc.

print('Searching for all section markers between inventory start and building_trader@31:')
print('-' * 80)
print()

# Find all dot-prefixed sections
section_pattern = rb'\.[a-z]+'
matches = list(re.finditer(section_pattern, chunk))

print(f'Found {len(matches)} section markers')
print()

sections_found = []
for match in matches:
	section_name = match.group(0).decode('ascii')
	offset = match.start()
	abs_pos = search_start + offset
	distance_from_building = abs_pos - building_31_pos

	# Only show sections before building_trader@31
	if distance_from_building < 0:
		sections_found.append((section_name, abs_pos, distance_from_building))

print('Sections BEFORE building_trader@31 (sorted by position):')
for section_name, abs_pos, distance in sorted(sections_found, key=lambda x: x[1]):
	print(f'  {section_name:20s} at position {abs_pos} (offset {distance:+d})')

print()
print('=' * 80)
print()

# Show detailed content for each unique section type
print('DETAILED VIEW OF EACH SECTION:')
print('=' * 80)
print()

unique_sections = sorted(set(s[0] for s in sections_found))

for section_name in unique_sections:
	print(f'\nSection: {section_name}')
	print('-' * 60)

	# Find first occurrence of this section before building_trader@31
	section_bytes = section_name.encode('ascii')
	pos = chunk.rfind(section_bytes, 0, building_31_pos - search_start)

	if pos != -1:
		abs_pos = search_start + pos

		# Show 200 bytes of content
		content = chunk[pos:pos + 200]

		print(f'Position: {abs_pos}')
		print(f'Hex: {content.hex()[:100]}...')
		print(f'ASCII: {content.decode("ascii", errors="ignore")[:150]}')

print()
print('=' * 80)
print()

# Show the FULL structure from .shopunits to building_trader@31
print('COMPLETE STRUCTURE FROM .shopunits TO building_trader@31:')
print('=' * 80)
print()

shopunits_pos = data.rfind(b'.shopunits', building_31_pos - 2000, building_31_pos)
if shopunits_pos != -1:
	full_structure = data[shopunits_pos:building_31_pos + 50]

	print(f'Length: {len(full_structure)} bytes')
	print()
	print('ASCII decode:')
	print(full_structure.decode('ascii', errors='ignore'))

print()
print('=' * 80)
