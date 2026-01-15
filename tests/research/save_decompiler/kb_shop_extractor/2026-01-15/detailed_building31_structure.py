#!/usr/bin/env python3
"""Detailed byte-by-byte analysis of building_trader@31 structure"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('DETAILED STRUCTURE ANALYSIS: building_trader@31')
print('=' * 80)
print()

building_31_pos = 669916

print(f'building_trader@31 position: {building_31_pos}')
print()

# Extract 500 bytes starting from building_trader@31
chunk = data[building_31_pos:building_31_pos + 500]

print('RAW HEX (first 200 bytes):')
print('-' * 80)
print(chunk[:200].hex())
print()

print('=' * 80)
print()

print('BYTE-BY-BYTE PARSING:')
print('-' * 80)
print()

# Parse the structure field by field
pos = 0

# 1. "building_trader@31" string
marker_end = chunk.find(b'\x00', pos)
if marker_end != -1:
	marker = chunk[pos:marker_end].decode('ascii', errors='ignore')
	print(f'[{pos:3d}] Marker: "{marker}"')
	pos = marker_end + 1

# 2. Padding/alignment bytes
while pos < len(chunk) and chunk[pos] == 0:
	pos += 1

print(f'[{pos:3d}] (skipped {pos - marker_end - 1} null bytes)')

# 3. Following structure - let's parse each 4-byte value
print()
print('Following 4-byte integers:')
print('-' * 40)

for i in range(20):
	if pos + 4 > len(chunk):
		break

	value = struct.unpack('<I', chunk[pos:pos+4])[0]
	print(f'[{building_31_pos + pos:6d}] +{pos:3d}: {value:12d} (0x{value:08x})')

	# Check if this could be related to actor ID
	if value > 100000000 and value < 3000000000:
		print(f'        ^^^ LARGE NUMBER - could be actor ID or hash!')

	pos += 4

print()
print('=' * 80)
print()

# Show the same data but try to identify known patterns
print('FIELD IDENTIFICATION:')
print('-' * 80)
print()

# Reset position
pos = len(b'building_trader@31\x00')

# Skip padding
while pos < len(chunk) and chunk[pos] == 0:
	pos += 1

# Common fields we've seen before:
# - auid (actor unique id - but this is instance ID, not actor type ID)
# - pos (position coordinates)
# - flags
# - vars

# Look for known field markers
field_markers = [b'auid', b'pos', b'flags', b'vars', b'guid', b'bmd']

for marker in field_markers:
	marker_pos = chunk.find(marker)
	if marker_pos != -1:
		print(f'Found "{marker.decode()}" at offset {marker_pos}')

		# Try to extract value after marker
		value_pos = marker_pos + len(marker) + 1  # Skip marker and type byte
		if value_pos + 4 <= len(chunk):
			value = struct.unpack('<I', chunk[value_pos:value_pos+4])[0]
			print(f'  Value: {value} (0x{value:08x})')

print()
print('=' * 80)
