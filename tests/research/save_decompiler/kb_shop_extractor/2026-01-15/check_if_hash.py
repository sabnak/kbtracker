#!/usr/bin/env python3
"""Check if .actors strg value is a hash of actor name/ID"""

import zlib
import hashlib

print('=' * 80)
print('CHECKING IF .actors VALUE IS A HASH')
print('=' * 80)
print()

# Values from .actors fields
value_31 = 0x3b84bcee  # building_trader@31 (should be actor_807991996)
value_818 = 0xafa07a85  # building_trader@818 (lookup says actor_807991996)

print(f'building_trader@31 .actors value:  0x{value_31:08x} ({value_31})')
print(f'building_trader@818 .actors value: 0x{value_818:08x} ({value_818})')
print()

# Test various string formats that might be hashed
test_strings = [
	'807991996',
	'actor_807991996',
	'actor_system_807991996',
	'actor_system_807991996_name',
	'818',
	'31',
	'building_trader@31',
	'building_trader@818',
]

print('Testing if CRC32 matches:')
print('-' * 60)

for s in test_strings:
	crc = zlib.crc32(s.encode('utf-8')) & 0xffffffff
	print(f'  CRC32("{s}"): 0x{crc:08x}', end='')

	if crc == value_31:
		print(f' ★★★ MATCHES building_trader@31!')
	elif crc == value_818:
		print(f' ★★★ MATCHES building_trader@818!')
	else:
		print()

print()
print('Testing other hash algorithms:')
print('-' * 60)

for s in ['807991996', 'actor_807991996', '31', '818']:
	md5 = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
	print(f'  MD5("{s}")[:4]: 0x{md5:08x}', end='')

	if md5 == value_31:
		print(f' ★★★ MATCHES!')
	elif md5 == value_818:
		print(f' ★★★ MATCHES!')
	else:
		print()

print()
print('=' * 80)
