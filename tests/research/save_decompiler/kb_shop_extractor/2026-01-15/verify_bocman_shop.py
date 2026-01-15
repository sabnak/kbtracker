#!/usr/bin/env python3
"""Verify which building_trader@ actually has the bocman inventory"""

from pathlib import Path
import re

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('VERIFYING WHICH SHOP HAS BOCMAN INVENTORY')
print('=' * 80)
print()

# Find bocman with quantity 1460
bocman_pos = data.find(b'bocman/1460/')

if bocman_pos == -1:
	print('bocman/1460/ not found!')
else:
	print(f'bocman/1460/ found at position {bocman_pos}')
	print()

	# Find ALL building_trader@ markers within 2000 bytes after bocman
	print('building_trader@ markers within 2000 bytes AFTER bocman:')
	print('-' * 80)

	search_end = min(len(data), bocman_pos + 2000)
	chunk_after = data[bocman_pos:search_end]

	pattern = rb'building_trader@(\d+)(?!\d)'
	matches_after = list(re.finditer(pattern, chunk_after))

	if matches_after:
		for match in matches_after:
			building_num = match.group(1).decode('ascii')
			offset = match.start()
			abs_pos = bocman_pos + offset

			print(f'  building_trader@{building_num} at offset +{offset} (position {abs_pos})')

			# Check if this is followed by shopunits or other sections
			context = chunk_after[offset:offset+100]
			if b'.shopunits' in context or b'.spells' in context:
				print(f'    → Has inventory sections nearby (NOT the shop marker)')
			else:
				print(f'    → Likely the shop identifier')
	else:
		print('  None found')

	print()

	# Find closest building_trader@ marker BEFORE bocman (this is unusual but let's check)
	print('building_trader@ markers within 2000 bytes BEFORE bocman:')
	print('-' * 80)

	search_start = max(0, bocman_pos - 2000)
	chunk_before = data[search_start:bocman_pos]

	matches_before = list(re.finditer(pattern, chunk_before))

	if matches_before:
		# Get the LAST one (closest to bocman)
		for match in matches_before[-3:]:  # Show last 3
			building_num = match.group(1).decode('ascii')
			offset = match.start()
			abs_pos = search_start + offset

			print(f'  building_trader@{building_num} at offset {offset - len(chunk_before)} (position {abs_pos})')
	else:
		print('  None found')

	print()
	print('=' * 80)
	print()

	# Now find the CLOSEST building_trader@ after bocman that's NOT inside inventory sections
	print('DETERMINING THE ACTUAL SHOP IDENTIFIER:')
	print('-' * 80)
	print()

	# Strategy: Find building_trader@ that comes after .shopunits/.spells/.temp sections
	# This should be the shop identifier

	shopunits_pos = data.rfind(b'.shopunits', bocman_pos - 1000, bocman_pos + 100)
	if shopunits_pos != -1:
		print(f'.shopunits found at position {shopunits_pos} (offset {shopunits_pos - bocman_pos} from bocman)')

		# Find building_trader@ after .shopunits but after the inventory sections
		temp_pos = data.find(b'.temp', shopunits_pos)
		if temp_pos != -1 and temp_pos < bocman_pos + 2000:
			print(f'.temp found at position {temp_pos}')

			# Find building_trader@ after .temp
			search_after_temp = data[temp_pos:temp_pos + 500]
			bt_match = re.search(rb'building_trader@(\d+)(?!\d)', search_after_temp)

			if bt_match:
				building_num = bt_match.group(1).decode('ascii')
				abs_pos = temp_pos + bt_match.start()

				print()
				print(f'✓ Shop identifier: building_trader@{building_num} at position {abs_pos}')
				print(f'  (This is {abs_pos - bocman_pos} bytes after bocman)')

	print()
	print('=' * 80)
