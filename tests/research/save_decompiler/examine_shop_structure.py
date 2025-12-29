#!/usr/bin/env python3
"""
Examine the data structure around shop locations
"""
import struct


def examine_shop_data(file_path: str, shop_name: str):
	"""Examine data structure around a shop location"""
	with open(file_path, 'rb') as f:
		data = f.read()

	# Find all occurrences of the shop name
	text = data.decode('ascii', errors='ignore')
	occurrences = []

	start = 0
	while True:
		pos = text.find(shop_name, start)
		if pos == -1:
			break
		occurrences.append(pos)
		start = pos + 1

	print(f"=== Examining '{shop_name}' ===\n")
	print(f"Found {len(occurrences)} occurrences\n")

	# Examine first few occurrences
	for i, text_pos in enumerate(occurrences[:5]):
		print(f"[Occurrence {i+1}] Text offset: {text_pos}")

		# Find actual byte offset
		byte_pos = find_byte_offset(data, shop_name)
		if byte_pos == -1:
			continue

		print(f"                Byte offset: {byte_pos:08x}")

		# Show structure before the string
		show_structure_before(data, byte_pos, shop_name)

		# Show structure after the string
		show_structure_after(data, byte_pos, shop_name)

		print()


def find_byte_offset(data: bytes, pattern: str) -> int:
	"""Find byte offset of ASCII pattern"""
	pattern_bytes = pattern.encode('ascii')
	return data.find(pattern_bytes)


def show_structure_before(data: bytes, offset: int, shop_name: str):
	"""Show structure before the shop name"""
	# Check if there's a length prefix
	if offset >= 4:
		length = struct.unpack('<I', data[offset-4:offset])[0]
		print(f"  Length prefix: {length} (expected: {len(shop_name)})")

		if length == len(shop_name):
			# This is likely a length-prefixed string
			# Look further back for context
			if offset >= 20:
				prev_data = data[offset-20:offset-4]
				print(f"  20 bytes before length:")
				hex_dump(prev_data, offset-20)


def show_structure_after(data: bytes, offset: int, shop_name: str):
	"""Show structure after the shop name"""
	start = offset + len(shop_name)
	end = min(len(data), start + 128)
	chunk = data[start:end]

	print(f"  128 bytes after shop name:")
	hex_dump(chunk, start)

	# Try to parse as structured data
	print(f"\n  Attempting to parse structure:")
	try:
		pos = 0
		# First 4 bytes might be count or size
		if len(chunk) >= 4:
			val1 = struct.unpack('<I', chunk[pos:pos+4])[0]
			print(f"    +0x00: {val1:10d} (0x{val1:08x})")
			pos += 4

			if len(chunk) >= 8:
				val2 = struct.unpack('<I', chunk[pos:pos+4])[0]
				print(f"    +0x04: {val2:10d} (0x{val2:08x})")
				pos += 4

			# Check if next looks like a length-prefixed string
			if pos + 4 < len(chunk):
				str_len = struct.unpack('<I', chunk[pos:pos+4])[0]
				if 0 < str_len < 200:
					print(f"    +0x{pos:02x}: Possible string length: {str_len}")
					if pos + 4 + str_len < len(chunk):
						try:
							string = chunk[pos+4:pos+4+str_len].decode('ascii')
							print(f"           String: '{string}'")
							pos += 4 + str_len
						except:
							pass

	except Exception as e:
		print(f"    Parse error: {e}")


def hex_dump(data: bytes, base_offset: int):
	"""Print hex dump with offset"""
	for i in range(0, len(data), 16):
		chunk = data[i:min(i+16, len(data))]
		hex_part = ' '.join(f'{b:02x}' for b in chunk)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
		print(f"    {base_offset+i:08x}: {hex_part:48s} {ascii_part}")


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	# Examine a specific shop location
	examine_shop_data(decompressed_file, 'm_galenirimm')
