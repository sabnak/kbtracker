#!/usr/bin/env python3
"""Verify that strg value with last byte cleared gives actor ID"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('EXTRACTING ACTOR ID FROM .actors strg VALUE')
print('=' * 80)
print()

def extract_actor_id_from_strg(strg_value):
	"""Extract actor ID by clearing bit 7 of last byte"""
	# Convert to bytes
	strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))

	# Clear bit 7 of last byte (0x80 bit)
	actor_bytes = list(strg_bytes)
	actor_bytes[3] = actor_bytes[3] & 0x7F  # Clear bit 7

	# Convert back to integer
	actor_id = struct.unpack('<I', bytes(actor_bytes))[0]

	return actor_id

# Test with building_trader@31
print('building_trader@31:')
print('-' * 60)

actors_31_pos = 669357
chunk_31 = data[actors_31_pos:actors_31_pos + 60]
strg_pos = chunk_31.find(b'strg')
strg_value_31 = struct.unpack('<I', chunk_31[strg_pos + 8:strg_pos + 12])[0]

actor_id_31 = extract_actor_id_from_strg(strg_value_31)

print(f'strg value:   0x{strg_value_31:08x} ({strg_value_31})')
print(f'Extracted actor ID: {actor_id_31}')
print()

if actor_id_31 == 807991996:
	print('★★★ SUCCESS! Extracted actor_807991996!')
else:
	print(f'Expected 807991996, got {actor_id_31}')

print()
print('=' * 80)
print()

# Test with building_trader@818
print('building_trader@818:')
print('-' * 60)

building_818_pos = 741202
actors_818_pos = data.find(b'.actors', building_818_pos - 500)

if actors_818_pos != -1 and actors_818_pos < building_818_pos:
	chunk_818 = data[actors_818_pos:actors_818_pos + 60]
	strg_pos = chunk_818.find(b'strg')

	if strg_pos != -1:
		strg_value_818 = struct.unpack('<I', chunk_818[strg_pos + 8:strg_pos + 12])[0]
		actor_id_818 = extract_actor_id_from_strg(strg_value_818)

		print(f'strg value:   0x{strg_value_818:08x} ({strg_value_818})')
		print(f'Extracted actor ID: {actor_id_818}')
		print()

		# Lookup table says building_trader@818 should be actor_807991996
		if actor_id_818 == 807991996:
			print('✓ Matches lookup table (actor_807991996)')
		else:
			print(f'Lookup table says actor_807991996, extracted {actor_id_818}')
else:
	print('Could not find .actors section before building_trader@818')

print()
print('=' * 80)
