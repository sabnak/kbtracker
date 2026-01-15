#!/usr/bin/env python3
"""Check all location tags around the bocman/building_trader@31 area"""

from pathlib import Path
import struct
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('ANALYZING LOCATION TAGS AROUND bocman/building_trader@31')
print('=' * 80)
print()

bocman_pos = 669460
building_31_pos = 669916

print(f'bocman position: {bocman_pos}')
print(f'building_trader@31 position: {building_31_pos}')
print(f'Distance: {building_31_pos - bocman_pos} bytes')
print()

# Search for ALL 'lt' tags in a wider area
search_start = bocman_pos - 2000
search_end = building_31_pos + 500

print(f'Searching for "lt" tags between {search_start} and {search_end}')
print('=' * 80)
print()

chunk = data[search_start:search_end]

# Find all 'lt' occurrences
lt_positions = []
pos = 0
while True:
	pos = chunk.find(b'lt', pos)
	if pos == -1:
		break
	lt_positions.append(pos)
	pos += 1

print(f'Found {len(lt_positions)} "lt" occurrences in this range')
print()

# Process each 'lt' and try to extract location name
for i, lt_pos in enumerate(lt_positions):
	abs_pos = search_start + lt_pos

	try:
		# Check if this is actually a location tag (has 4-byte length after 'lt')
		length_bytes = chunk[lt_pos + 2:lt_pos + 6]
		if len(length_bytes) == 4:
			location_length = struct.unpack('<I', length_bytes)[0]

			# Sanity check
			if 1 < location_length < 100:
				location_start = lt_pos + 6
				location_bytes = chunk[location_start:location_start + location_length]

				# Try ASCII decode
				try:
					location = location_bytes.decode('ascii')
					distance_to_bocman = abs_pos - bocman_pos
					distance_to_building = abs_pos - building_31_pos

					print(f'{i+1}. Position {abs_pos}:')
					print(f'   Location: "{location}"')
					print(f'   Distance to bocman: {distance_to_bocman:+d} bytes')
					print(f'   Distance to building_trader@31: {distance_to_building:+d} bytes')

					# Show what comes immediately after
					after_location = lt_pos + 6 + location_length
					after_chunk = chunk[after_location:after_location + 50]
					after_text = after_chunk.decode('ascii', errors='ignore')
					print(f'   After location: {after_text[:50]}')
					print()
				except:
					pass
	except:
		pass

print('=' * 80)
print()

# Also check for any itext_ references in this area
print('Checking for itext_ shop identifiers:')
print('-' * 80)

itext_pattern = rb'itext_.*?_\d+'
matches = list(re.finditer(itext_pattern, chunk))

if matches:
	for match in matches[:10]:
		pos_in_chunk = match.start()
		abs_pos = search_start + pos_in_chunk
		distance_to_bocman = abs_pos - bocman_pos
		distance_to_building = abs_pos - building_31_pos

		# Try UTF-16-LE decode
		try:
			text = match.group(0).decode('utf-16-le', errors='ignore')
			print(f'  {abs_pos}: {text}')
			print(f'    Distance to bocman: {distance_to_bocman:+d}')
			print(f'    Distance to building_trader@31: {distance_to_building:+d}')
			print()
		except:
			pass
else:
	print('  No itext_ identifiers found in this area')

print('=' * 80)
