#!/usr/bin/env python3
"""Extract actor ID from building_trader@818's .actors section"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('EXTRACTING ACTOR ID FROM building_trader@818')
print('=' * 80)
print()

def extract_actor_id_from_strg(strg_value):
	"""Extract actor ID by clearing bit 7 of last byte"""
	strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))
	actor_bytes = list(strg_bytes)
	actor_bytes[3] = actor_bytes[3] & 0x7F  # Clear bit 7
	actor_id = struct.unpack('<I', bytes(actor_bytes))[0]
	return actor_id

# building_trader@818 is at position 741202
# .actors section is at position 739118 (2084 bytes before)
actors_pos = 739118
building_pos = 741202

print(f'building_trader@818 at position: {building_pos}')
print(f'.actors section at position: {actors_pos}')
print(f'Distance: {building_pos - actors_pos} bytes')
print()

# Extract .actors section content
chunk = data[actors_pos:actors_pos + 100]

print('HEX DUMP of .actors section:')
print('-' * 80)
print(chunk.hex())
print()

print('ASCII DECODE:')
print('-' * 80)
print(chunk.decode('ascii', errors='ignore'))
print()

# Find strg marker
strg_pos = chunk.find(b'strg')

if strg_pos == -1:
	print('strg marker not found!')
else:
	print(f'strg marker found at offset {strg_pos}')
	print()

	# strg structure: 'strg' (4 bytes) + length (4 bytes) + value (4 bytes)
	value_offset = strg_pos + 8
	if value_offset + 4 <= len(chunk):
		strg_value = struct.unpack('<I', chunk[value_offset:value_offset + 4])[0]
		actor_id = extract_actor_id_from_strg(strg_value)

		print(f'strg value: 0x{strg_value:08x} ({strg_value})')
		print(f'Extracted actor ID: {actor_id}')
		print()

		# Check byte structure
		strg_bytes = struct.unpack('4B', struct.pack('<I', strg_value))
		actor_bytes = struct.unpack('4B', struct.pack('<I', actor_id))

		print('Byte comparison:')
		print(f'  strg bytes:  {" ".join(f"{b:02x}" for b in strg_bytes)} = {list(strg_bytes)}')
		print(f'  actor bytes: {" ".join(f"{b:02x}" for b in actor_bytes)} = {list(actor_bytes)}')
		print(f'  Last byte diff: 0x{strg_bytes[3]:02x} vs 0x{actor_bytes[3]:02x} (bit 7 cleared)')

print()
print('=' * 80)
