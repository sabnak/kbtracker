"""Analyze the structure around 'moral' entries to understand what they are"""
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

# Find .items section
items_marker = b'.items'
search_start = max(0, shop_pos - 5000)
items_pos = data.rfind(items_marker, search_start, shop_pos)

print(f'Shop at position {shop_pos}')
print(f'.items section at position {items_pos}')
print()

# Find both "moral" occurrences
moral_bytes = b'moral'
occurrences = []
pos = items_pos
while pos < shop_pos:
	found_pos = data.find(moral_bytes, pos, shop_pos)
	if found_pos == -1:
		break

	# Check if length-prefixed
	if found_pos >= 4:
		length_bytes = data[found_pos - 4:found_pos]
		length = int.from_bytes(length_bytes, 'little')
		if length == 5:
			occurrences.append(found_pos)

	pos = found_pos + 1

print(f'Found {len(occurrences)} "moral" occurrences\n')

# Analyze structure around each occurrence
for i, occ_pos in enumerate(occurrences, 1):
	print('=' * 80)
	print(f'OCCURRENCE {i} at position {occ_pos}')
	print('=' * 80)

	# Show 200 bytes before and after
	context_start = max(0, occ_pos - 200)
	context_end = min(len(data), occ_pos + 200)
	context = data[context_start:context_end]

	# Try to parse backwards to find the actual item name
	print('\nSearching backwards for length-prefixed strings:\n')

	search_back_start = max(0, occ_pos - 150)
	pos_back = occ_pos - 4  # Start before "moral" length prefix

	strings_found = []
	while pos_back > search_back_start:
		# Try to read a length prefix
		if pos_back >= 4:
			potential_length_pos = pos_back - 4
			potential_length = int.from_bytes(data[potential_length_pos:pos_back], 'little')

			# Check if this looks like a valid string
			if 3 <= potential_length <= 100:
				potential_string_start = pos_back
				potential_string_end = pos_back + potential_length

				if potential_string_end <= len(data):
					try:
						potential_string = data[potential_string_start:potential_string_end].decode('ascii')
						# Check if it's all lowercase/alphanumeric
						if potential_string.replace('_', '').isalnum() and potential_string.islower():
							relative_pos = potential_string_start - occ_pos
							strings_found.append({
								'pos': potential_string_start,
								'relative': relative_pos,
								'length': potential_length,
								'string': potential_string
							})
					except:
						pass

		pos_back -= 1

	# Show found strings
	strings_found.reverse()  # Show in chronological order
	for s in strings_found:
		print(f'  Position {s["pos"]} (offset {s["relative"]:+d}): "{s["string"]}" (length {s["length"]})')

	print('\nSearching forwards for length-prefixed strings:\n')

	pos_forward = occ_pos + 5  # After "moral"
	search_forward_end = min(len(data), occ_pos + 150)

	strings_forward = []
	while pos_forward < search_forward_end:
		# Try to read a length prefix
		if pos_forward + 4 <= len(data):
			potential_length = int.from_bytes(data[pos_forward:pos_forward + 4], 'little')

			# Check if this looks like a valid string
			if 2 <= potential_length <= 100:
				potential_string_start = pos_forward + 4
				potential_string_end = potential_string_start + potential_length

				if potential_string_end <= len(data):
					try:
						potential_string = data[potential_string_start:potential_string_end].decode('ascii')
						# Any printable ASCII
						if all(32 <= ord(c) <= 126 for c in potential_string):
							relative_pos = potential_string_start - occ_pos
							strings_forward.append({
								'pos': potential_string_start,
								'relative': relative_pos,
								'length': potential_length,
								'string': potential_string
							})
							pos_forward = potential_string_end
							continue
					except:
						pass

		pos_forward += 1

	for s in strings_forward[:10]:  # Show first 10
		print(f'  Position {s["pos"]} (offset {s["relative"]:+d}): "{s["string"]}" (length {s["length"]})')

	# Show hex dump around "moral"
	print('\nHex dump (100 bytes before and after "moral"):\n')
	hex_start = max(0, occ_pos - 100)
	hex_end = min(len(data), occ_pos + 100)
	hex_data = data[hex_start:hex_end]

	offset = 0
	while offset < len(hex_data):
		chunk = hex_data[offset:offset + 16]

		# Hex representation
		hex_repr = ' '.join(f'{b:02x}' for b in chunk)
		hex_repr = hex_repr.ljust(48)

		# ASCII representation
		ascii_repr = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)

		# Highlight "moral"
		abs_pos = hex_start + offset
		marker = '>>>' if abs_pos <= occ_pos < abs_pos + 16 else '   '

		print(f'{marker} {abs_pos:06d}  {hex_repr}  {ascii_repr}')
		offset += 16

	print('\n')

# Now check if "moral" appears in metadata keywords
from src.utils.parsers.save_data.ShopInventoryParserOld import ShopInventoryParserOld

parser = ShopInventoryParserOld(
	decompressor=None,
	item_repository=None,
	spell_repository=None,
	unit_repository=None,
	shop_repository=None,
	shop_inventory_repository=None
)

print('=' * 80)
print('METADATA KEYWORDS CHECK')
print('=' * 80)
print(f'Is "moral" in METADATA_KEYWORDS? {"moral" in parser.METADATA_KEYWORDS}')
print(f'METADATA_KEYWORDS: {parser.METADATA_KEYWORDS}')
