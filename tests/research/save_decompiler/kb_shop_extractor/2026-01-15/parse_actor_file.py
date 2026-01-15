#!/usr/bin/env python3
"""Parse actor .act file to understand its structure"""

from pathlib import Path
import struct

actor_file = Path('F:/var/kbtracker/tests/game_files/actors/807991996.act')

with open(actor_file, 'rb') as f:
	data = f.read()

print('=' * 80)
print('PARSING ACTOR FILE: 807991996.act')
print('=' * 80)
print()

print(f'File size: {len(data)} bytes')
print()

# Show hex dump
print('Hex dump:')
print('-' * 80)
print(data.hex())
print()

print('=' * 80)
print()

# Try to parse the structure
print('Parsing structure:')
print('-' * 80)
print()

pos = 0

# Skip initial bytes
while pos < len(data):
	# Look for string markers (like 'uid', 'fn', 'fd', 'fp', 'ml', etc.)
	# These seem to be 2-character tags followed by data

	# Try to read as 2-byte tag
	if pos + 2 > len(data):
		break

	tag = data[pos:pos+2].decode('ascii', errors='ignore')

	if tag in ['ui', 'fn', 'fd', 'fp', 'mi', 'ml']:
		print(f'Position {pos}: Tag "{tag}"')

		# Skip tag
		pos += 2

		if tag == 'ui':
			# UID might be followed by 'd' and then 4-byte integer
			if pos < len(data) and data[pos] == ord('d'):
				pos += 1  # Skip 'd'
				if pos + 4 <= len(data):
					uid_value = struct.unpack('<I', data[pos:pos+4])[0]
					print(f'  Value (4-byte int): {uid_value}')
					pos += 4

		elif tag in ['fn', 'fd', 'fp', 'ml']:
			# These are followed by strings
			# Find the string (terminated by space, newline, or another tag)
			string_start = pos

			# Read until we hit another 2-char tag or end
			string_end = string_start
			while string_end < len(data):
				# Check if we're at the start of a new tag
				if string_end + 2 <= len(data):
					potential_tag = data[string_end:string_end+2].decode('ascii', errors='ignore')
					if potential_tag in ['ui', 'fn', 'fd', 'fp', 'mi', 'ml']:
						break
				string_end += 1

			string_value = data[string_start:string_end].decode('utf-16-le', errors='ignore').rstrip('\x00 \n')
			print(f'  Value (string): "{string_value}"')
			pos = string_end

		elif tag == 'mi':
			# Might be followed by integer
			if pos + 4 <= len(data):
				mi_value = struct.unpack('<I', data[pos:pos+4])[0]
				print(f'  Value (4-byte int): {mi_value}')
				pos += 4

		print()
	else:
		pos += 1

print('=' * 80)
print()

# Manual extraction of the location
print('KEY FINDINGS:')
print('-' * 80)
print()

# Find 'ml' tag
ml_pos = data.find(b'ml')
if ml_pos != -1:
	# Extract location after 'ml'
	location_start = ml_pos + 2
	location_bytes = data[location_start:location_start + 20]

	# Try UTF-16-LE
	try:
		location = location_bytes.decode('utf-16-le', errors='ignore').split('\x00')[0]
		print(f'✓ Location (ml tag): "{location}"')
	except:
		location = location_bytes.decode('ascii', errors='ignore').split('\x00')[0]
		print(f'✓ Location (ml tag): "{location}"')

# Find the actor ID at the beginning
uid_pos = data.find(b'uid')
if uid_pos != -1:
	# Skip 'uid' and 'd', then read 4 bytes
	id_start = uid_pos + 4
	if id_start + 4 <= len(data):
		actor_id = struct.unpack('<I', data[id_start:id_start+4])[0]
		print(f'✓ Actor ID (uid): {actor_id}')

print()
print('=' * 80)
