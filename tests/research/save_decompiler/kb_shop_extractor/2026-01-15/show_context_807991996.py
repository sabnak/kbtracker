#!/usr/bin/env python3
"""Show all context around 807991996 in the save file"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('CONTEXT AROUND 807991996')
print('=' * 80)
print()

target = 807991996

# 1. Search as ASCII text
print('1. As ASCII text "807991996":')
print('-' * 80)
ascii_pattern = b'807991996'
pos = 0
count = 0
while True:
	pos = data.find(ascii_pattern, pos)
	if pos == -1:
		break
	count += 1

	print(f'\nOccurrence {count} at position {pos}:')

	# Show 500 bytes before and after
	start = max(0, pos - 500)
	end = min(len(data), pos + 500)
	chunk = data[start:end]

	print('\nASCII decode:')
	print(chunk.decode('ascii', errors='ignore'))
	print()
	print('HEX (first 200 bytes):')
	print(chunk[:200].hex())

	pos += 1

print()
print('=' * 80)
print()

# 2. Search as little-endian binary
print('2. As little-endian 4-byte integer:')
print('-' * 80)
le_bytes = struct.pack('<I', target)
print(f'Bytes: {le_bytes.hex()}')
pos = 0
count = 0
while True:
	pos = data.find(le_bytes, pos)
	if pos == -1:
		break
	count += 1

	print(f'\nOccurrence {count} at position {pos}:')

	# Show 200 bytes before and after
	start = max(0, pos - 200)
	end = min(len(data), pos + 200)
	chunk = data[start:end]

	print('\nASCII decode:')
	print(chunk.decode('ascii', errors='ignore'))
	print()
	print('HEX:')
	print(chunk.hex())

	pos += 1

if count == 0:
	print('NOT FOUND as little-endian binary')

print()
print('=' * 80)
print()

# 3. Search as big-endian binary
print('3. As big-endian 4-byte integer:')
print('-' * 80)
be_bytes = struct.pack('>I', target)
print(f'Bytes: {be_bytes.hex()}')
pos = 0
count = 0
while True:
	pos = data.find(be_bytes, pos)
	if pos == -1:
		break
	count += 1

	print(f'\nOccurrence {count} at position {pos}:')

	# Show 200 bytes before and after
	start = max(0, pos - 200)
	end = min(len(data), pos + 200)
	chunk = data[start:end]

	print('\nASCII decode:')
	print(chunk.decode('ascii', errors='ignore'))
	print()
	print('HEX:')
	print(chunk.hex())

	pos += 1

if count == 0:
	print('NOT FOUND as big-endian binary')

print()
print('=' * 80)
