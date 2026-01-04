"""Investigate duplicate 'moral' item in shop zcom_519"""
from pathlib import Path as FilePath
import sys

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

# Decompressor
decompressor = SaveFileDecompressor()
save_path = FilePath('/app/tests/game_files/saves/1707047253/data')
data = decompressor.decompress(save_path)

# Find shop zcom_519
shop_id = "itext_m_zcom_519"
shop_id_bytes = shop_id.encode('utf-16-le')
shop_pos = data.find(shop_id_bytes)

if shop_pos == -1:
	print(f'Shop {shop_id} not found')
	sys.exit(1)

print(f'Shop "{shop_id}" found at position {shop_pos}')

# Find .items section
items_marker = b'.items'
search_start = max(0, shop_pos - 5000)
items_pos = data.rfind(items_marker, search_start, shop_pos)

if items_pos == -1:
	print('.items section not found')
	sys.exit(1)

print(f'.items section at position {items_pos}')

# Search for all occurrences of "moral" in the items section area
moral_bytes = b'moral'
search_area_start = items_pos
search_area_end = shop_pos

print(f'\nSearching for "moral" between positions {search_area_start} and {search_area_end}')

occurrences = []
pos = search_area_start
while pos < search_area_end:
	found_pos = data.find(moral_bytes, pos, search_area_end)
	if found_pos == -1:
		break

	# Check if this is a length-prefixed string
	# Length prefix is 4 bytes before the string
	if found_pos >= 4:
		length_bytes = data[found_pos - 4:found_pos]
		length = int.from_bytes(length_bytes, 'little')

		# Check if length matches "moral" (5 characters)
		if length == 5:
			occurrences.append({
				'position': found_pos,
				'length_prefix_pos': found_pos - 4,
				'length': length,
				'context_before': data[found_pos - 20:found_pos].hex(' '),
				'context_after': data[found_pos + 5:found_pos + 25].hex(' ')
			})

	pos = found_pos + 1

print(f'\nFound {len(occurrences)} occurrence(s) of "moral" with valid length prefix:\n')

for i, occ in enumerate(occurrences, 1):
	print(f'Occurrence {i}:')
	print(f'  Position: {occ["position"]} (length prefix at {occ["length_prefix_pos"]})')
	print(f'  Length prefix value: {occ["length"]}')
	print(f'  Context before (20 bytes): {occ["context_before"]}')
	print(f'  String: "moral"')
	print(f'  Context after (20 bytes): {occ["context_after"]}')
	print()

# Also check what comes after each "moral"
print('\nParsing context for each occurrence:\n')

for i, occ in enumerate(occurrences, 1):
	print(f'Occurrence {i} at position {occ["position"]}:')

	# Try to parse what comes after "moral"
	after_pos = occ['position'] + 5

	# Check if there's metadata (4-byte count)
	if after_pos + 4 <= len(data):
		next_4_bytes = data[after_pos:after_pos + 4]
		as_int = int.from_bytes(next_4_bytes, 'little')
		print(f'  Next 4 bytes as int: {as_int}')
		print(f'  Next 4 bytes as hex: {next_4_bytes.hex(" ")}')

		# Check if next value looks like another length prefix
		if after_pos + 4 + 4 <= len(data):
			potential_length = int.from_bytes(data[after_pos + 4:after_pos + 8], 'little')
			if 3 <= potential_length <= 100:
				potential_name = data[after_pos + 8:after_pos + 8 + potential_length]
				try:
					name_str = potential_name.decode('ascii')
					print(f'  Potential next item: "{name_str}" (length {potential_length})')
				except:
					print(f'  Potential next item: (non-ASCII, length {potential_length})')
	print()

# Check if there's a .temp or other section marker between .items and shop ID
print('\nSearching for section markers between .items and shop ID:\n')

section_markers = [b'.items', b'.spells', b'.shopunits', b'.garrison', b'.temp', b'.misc']

for marker in section_markers:
	marker_pos = data.find(marker, items_pos + 1, shop_pos)
	if marker_pos != -1:
		relative_pos = marker_pos - items_pos
		print(f'  {marker.decode("ascii")} found at position {marker_pos} (offset +{relative_pos} from .items)')

print('\n' + '=' * 70)
print('CONCLUSION:')
print('=' * 70)

if len(occurrences) == 1:
	print('Only ONE "moral" entry found in binary data.')
	print('The duplicate in parser output is a BUG in the parser.')
elif len(occurrences) == 2:
	print('TWO "moral" entries found in binary data.')
	print('The duplicate in parser output is CORRECT - save file has duplicate.')
else:
	print(f'{len(occurrences)} occurrences found - needs further investigation.')
