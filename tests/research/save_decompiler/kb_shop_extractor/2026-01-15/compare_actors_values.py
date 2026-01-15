#!/usr/bin/env python3
"""Compare values in .actors fields between building_trader@31 and @818"""

from pathlib import Path
import struct

data_file = Path('/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/decompressed_data.bin')
with open(data_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('COMPARING .actors FIELD VALUES')
print('=' * 80)
print()

# building_trader@31
actors_31 = 670042
chunk_31 = data[actors_31:actors_31 + 60]

# building_trader@818
building_818 = 741202
actors_818 = data.find(b'.actors', building_818)
chunk_818 = data[actors_818:actors_818 + 60]

print('building_trader@31 .actors field:')
print('-' * 60)
print('Hex:', chunk_31.hex())
print()

# Parse structure: after "strg" comes a 4-byte length, then a 4-byte value
strg_pos_31 = chunk_31.find(b'strg')
value_pos_31 = strg_pos_31 + 8  # strg(4) + length(4)
value_31 = struct.unpack('<I', chunk_31[value_pos_31:value_pos_31+4])[0]

print(f'Value after strg: {value_31} (0x{value_31:08x})')
print()

print('building_trader@818 .actors field:')
print('-' * 60)
print('Hex:', chunk_818.hex())
print()

strg_pos_818 = chunk_818.find(b'strg')
value_pos_818 = strg_pos_818 + 8
value_818 = struct.unpack('<I', chunk_818[value_pos_818:value_pos_818+4])[0]

print(f'Value after strg: {value_818} (0x{value_818:08x})')
print()

print('=' * 80)
print('ANALYSIS:')
print('=' * 80)
print()

print(f'building_trader@31:  {value_31:10d} (0x{value_31:08x})')
print(f'building_trader@818: {value_818:10d} (0x{value_818:08x})')
print()
print(f'actor_807991996:     {807991996:10d} (0x{807991996:08x})')
print()

# Check various transformations
print('Checking transformations:')
print('-' * 40)

# Check if XOR gives actor ID
xor_31 = value_31 ^ 807991996
xor_818 = value_818 ^ 807991996

print(f'value_31 XOR actor_807991996:  0x{xor_31:08x}')
print(f'value_818 XOR actor_807991996: 0x{xor_818:08x}')
print()

# Check if these are indices into the lookup table
print(f'If value is an index into lookup table at 2.16M:')
print(f'  value_31 as offset:  2160000 + {value_31} = {2160000 + value_31}')
print(f'  value_818 as offset: 2160000 + {value_818} = {2160000 + value_818}')

print()
print('=' * 80)
