#!/usr/bin/env python3
"""Parse the strg value in .actors field"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('PARSING .actors FIELD STRUCTURE')
print('=' * 80)
print()

actors_pos = 670042

# Show the structure byte by byte
chunk = data[actors_pos:actors_pos + 60]

print('Byte-by-byte parsing:')
print('-' * 80)
print()

pos = 0

# ".actors" marker (7 bytes)
marker = chunk[pos:pos+7]
print(f'[{pos:2d}] Marker: {marker} = "{marker.decode()}"')
pos += 7

# Following structure
while pos < len(chunk) - 4:
	# Try to identify field markers
	if chunk[pos:pos+4] == b'flag':
		print(f'[{pos:2d}] Found "flags" marker')
		pos += 5  # "flags"

		# Next should be a value
		value = struct.unpack('<I', chunk[pos:pos+4])[0]
		print(f'[{pos:2d}]   flags value: {value}')
		pos += 4

	elif chunk[pos:pos+4] == b'strg':
		print(f'[{pos:2d}] Found "strg" marker')
		pos += 4

		# Next 4 bytes is the string value
		strg_value = struct.unpack('<I', chunk[pos:pos+4])[0]
		print(f'[{pos:2d}]   strg value: {strg_value} (0x{strg_value:08x})')
		pos += 4

		# This could be a hash or reference - let's check if it relates to our actor
		print(f'      Checking if this relates to actor_807991996...')

		# Check various relationships
		if strg_value == 807991996:
			print(f'      ★★★ EXACT MATCH to actor_807991996!')
		elif strg_value < 10000:
			print(f'      Could be an index or offset: {strg_value}')
		else:
			print(f'      Could be a hash or encoded value')

			# Check if XOR with some value gives us the actor ID
			target = 807991996
			xor_val = strg_value ^ target
			print(f'      XOR with actor_807991996: 0x{xor_val:08x}')

	else:
		# Read as 4-byte value
		if pos + 4 <= len(chunk):
			value = struct.unpack('<I', chunk[pos:pos+4])[0]
			if value < 256:
				print(f'[{pos:2d}] Small value: {value}')
			elif 100000000 <= value <= 2999999999:
				print(f'[{pos:2d}] Large value: {value} (0x{value:08x})')
		pos += 4

print()
print('=' * 80)
print()

# Compare with building_trader@818's .actors field
print('COMPARISON: building_trader@818 .actors field:')
print('-' * 80)

building_818_pos = 741202
actors_818_pos = data.find(b'.actors', building_818_pos)

if actors_818_pos != -1:
	chunk_818 = data[actors_818_pos:actors_818_pos + 60]

	# Find strg value
	strg_pos = chunk_818.find(b'strg')
	if strg_pos != -1:
		strg_value_818 = struct.unpack('<I', chunk_818[strg_pos+4:strg_pos+8])[0]
		print(f'building_trader@818 strg value: {strg_value_818} (0x{strg_value_818:08x})')
		print()

		print('Hex dump:')
		print(chunk_818.hex())

print()
print('=' * 80)
