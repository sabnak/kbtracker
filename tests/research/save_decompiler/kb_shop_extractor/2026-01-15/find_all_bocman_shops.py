#!/usr/bin/env python3
"""Find ALL shops with bocman quantity > 1000"""

from pathlib import Path
import sys
import re

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

def main():
	save_path = Path('/app/tests/game_files/saves/1768403991')

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_path)

	print('=' * 80)
	print('FINDING ALL SHOPS WITH bocman QUANTITY > 1000')
	print('=' * 80)
	print()

	# Pattern to find bocman with quantity
	# Format: bocman/{quantity}/
	pattern = rb'bocman/(\d+)/'
	matches = list(re.finditer(pattern, data))

	print(f'Found {len(matches)} occurrences of bocman')
	print()

	high_quantity_positions = []

	for match in matches:
		quantity = int(match.group(1))
		pos = match.start()

		if quantity > 1000:
			print(f'Position {pos}: bocman quantity = {quantity}')
			high_quantity_positions.append((pos, quantity))

			# Find nearest building_trader@ or itext_ AFTER this position
			search_chunk = data[pos:pos + 2000]

			# Look for building_trader@
			building_match = re.search(rb'building_trader@(\d+)', search_chunk)
			if building_match:
				building_num = building_match.group(1).decode('ascii')
				offset = building_match.start()
				print(f'  → building_trader@{building_num} at offset +{offset}')

			# Look for itext_
			itext_match = re.search(rb'itext_([-\w]+)_(\d+)', search_chunk)
			if itext_match:
				location = itext_match.group(1).decode('utf-16-le', errors='ignore')
				shop_id = itext_match.group(2).decode('utf-16-le', errors='ignore')
				offset = itext_match.start()
				print(f'  → itext_{location}_{shop_id} at offset +{offset}')

			# Extract location from lt tag BEFORE this position
			search_before = data[max(0, pos - 500):pos]
			lt_pos = search_before.rfind(b'lt')
			if lt_pos != -1:
				try:
					import struct
					abs_lt_pos = max(0, pos - 500) + lt_pos
					length_bytes = data[abs_lt_pos + 2:abs_lt_pos + 6]
					if len(length_bytes) == 4:
						location_length = struct.unpack('<I', length_bytes)[0]
						if location_length < 100:
							location_start = abs_lt_pos + 6
							location_bytes = data[location_start:location_start + location_length]
							location = location_bytes.decode('ascii', errors='ignore')
							print(f'  Location: {location}')
				except:
					pass

			print()

	print('=' * 80)
	print(f'Total high-quantity bocman shops: {len(high_quantity_positions)}')
	print('=' * 80)


if __name__ == '__main__':
	main()
