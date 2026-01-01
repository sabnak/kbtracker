#!/usr/bin/env python3
"""
Dump detailed binary structure of addon4_3_crystal to understand format
"""
import struct
import os


def hex_dump(data: bytes, offset: int, length: int, highlight_offset: int = -1) -> None:
	"""Print hex dump of data"""
	for i in range(0, length, 16):
		hex_part = ' '.join(f'{b:02x}' for b in data[offset+i:offset+i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset+i:offset+i+16])
		marker = ' <---' if highlight_offset != -1 and offset+i <= highlight_offset < offset+i+16 else ''
		print(f"{offset+i:08x}: {hex_part:48s} {ascii_part}{marker}")


if __name__ == '__main__':
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed_new.bin')

	with open(decompressed_file, 'rb') as f:
		data = f.read()

	# Find addon4_3_crystal
	target = b'addon4_3_crystal'
	pos = data.find(target)

	if pos == -1:
		print("addon4_3_crystal not found!")
		exit(1)

	print("="*78)
	print("BINARY STRUCTURE OF: addon4_3_crystal")
	print("="*78)
	print()

	# Find length field (4 bytes before name)
	name_length = len(target)
	length_pos = pos - 4

	stored_length = struct.unpack('<I', data[length_pos:length_pos+4])[0]
	print(f"Found at offset: {pos}")
	print(f"Length field at: {length_pos}")
	print(f"Stored length:   {stored_length}")
	print(f"Actual length:   {name_length}")
	print()

	if stored_length != name_length:
		print(f"[WARNING] Length mismatch! Searching for correct length field...")
		for back in range(4, 100, 4):
			test_pos = pos - back
			test_len = struct.unpack('<I', data[test_pos:test_pos+4])[0]
			if test_len == name_length:
				print(f"Found correct length at offset {test_pos} (back {back} bytes)")
				length_pos = test_pos
				break

	print()
	print("="*78)
	print("HEX DUMP: 200 bytes before name to 200 bytes after")
	print("="*78)
	print()

	dump_start = pos - 100
	dump_length = 300
	hex_dump(data, dump_start, dump_length, pos)

	print()
	print("="*78)
	print("STRUCTURE BREAKDOWN")
	print("="*78)
	print()

	# After name
	after_name_pos = pos + name_length
	print(f"Bytes after name (first 80 bytes):")
	for i in range(10):
		offset = after_name_pos + (i * 4)
		val = struct.unpack('<I', data[offset:offset+4])[0]
		hex_val = ' '.join(f'{b:02x}' for b in data[offset:offset+4])
		print(f"  +{i*4:2d} (offset {offset}): {val:10d} (0x{val:08x})  [{hex_val}]")

	# Try to parse as string
	print()
	print("Checking for embedded strings after name:")
	scan_pos = after_name_pos
	for _ in range(20):
		try:
			str_len = struct.unpack('<I', data[scan_pos:scan_pos+4])[0]
			if 1 <= str_len <= 100:
				try:
					maybe_str = data[scan_pos+4:scan_pos+4+str_len].decode('ascii', errors='strict')
					print(f"  At +{scan_pos - after_name_pos}: length={str_len}, string='{maybe_str}'")
					scan_pos += 4 + str_len
					continue
				except:
					pass
		except:
			pass
		scan_pos += 1
