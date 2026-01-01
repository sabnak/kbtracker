#!/usr/bin/env python3
"""
Analyze the structure of decompressed save data
"""
import struct


def analyze_structure(file_path: str):
	"""Analyze binary structure patterns"""
	with open(file_path, 'rb') as f:
		data = f.read()

	print("=== Binary Structure Analysis ===\n")
	print(f"Total size: {len(data):,} bytes\n")

	# Look for length-prefixed strings (common pattern)
	print("[1] Searching for length-prefixed strings...")
	strings_found = find_length_prefixed_strings(data, max_results=30)

	# Look for patterns with "itext" or "itm" without prefix
	print(f"\n[2] Searching for partial ID matches...")
	search_partial_ids(data)

	# Try UTF-16 encoding
	print(f"\n[3] Trying UTF-16 encoding...")
	try_utf16(data)

	# Look for numeric patterns that might be item/shop indices
	print(f"\n[4] Analyzing numeric sequences...")
	analyze_numeric_patterns(data)


def find_length_prefixed_strings(data: bytes, max_results: int = 20) -> list:
	"""Find strings with length prefix (common binary format)"""
	strings = []
	i = 0

	while i < len(data) - 4 and len(strings) < max_results:
		# Try reading as 32-bit little-endian length
		length = struct.unpack('<I', data[i:i+4])[0]

		# Reasonable string length (1-1000 chars)
		if 1 <= length <= 1000:
			try:
				string_data = data[i+4:i+4+length]
				# Try ASCII
				text = string_data.decode('ascii')
				if all(32 <= ord(c) < 127 or c == '\x00' for c in text):
					if len(text) > 3:  # Skip very short strings
						strings.append((i, length, text))
						print(f"    Offset {i:08x}: [{length:3d}] '{text}'")
						i += 4 + length
						continue
			except:
				pass

		i += 1

	return strings


def search_partial_ids(data: bytes):
	"""Search for partial ID patterns"""
	text = data.decode('ascii', errors='ignore')

	# Search for parts of shop/item names without prefix
	patterns = [
		'galenirimm',
		'helvedia',
		'grandpa_sword',
		'avrelii_gauntlet',
		'addon',
		'weapon',
		'gauntlet'
	]

	for pattern in patterns:
		count = text.count(pattern)
		if count > 0:
			offset = text.find(pattern)
			print(f"    [+] Found '{pattern}' {count} times (first at offset {offset})")
			# Show actual bytes around match
			byte_offset = find_byte_offset(data, text, offset)
			if byte_offset >= 0:
				show_bytes(data, byte_offset, pattern)
		else:
			print(f"    [-] Not found: '{pattern}'")


def try_utf16(data: bytes):
	"""Try decoding as UTF-16"""
	try:
		text = data.decode('utf-16-le', errors='ignore')

		# Search for patterns
		if 'itext_m_' in text:
			print(f"    [+] Found 'itext_m_' in UTF-16 text!")
			count = text.count('itext_m_')
			print(f"        Appears {count} times")
		elif 'itm_' in text:
			print(f"    [+] Found 'itm_' in UTF-16 text!")
			count = text.count('itm_')
			print(f"        Appears {count} times")
		else:
			print(f"    [-] No shop/item IDs found in UTF-16 encoding")

	except Exception as e:
		print(f"    [-] UTF-16 decode failed: {e}")


def analyze_numeric_patterns(data: bytes):
	"""Look for arrays of integers that might be item indices"""
	# Sample some 32-bit integers
	print(f"    First 20 32-bit integers (little-endian):")
	for i in range(0, min(80, len(data)), 4):
		val = struct.unpack('<I', data[i:i+4])[0]
		print(f"      Offset {i:04x}: {val:10d} (0x{val:08x})")


def find_byte_offset(data: bytes, text: str, text_offset: int) -> int:
	"""Find byte offset from text offset"""
	byte_count = 0
	for i in range(text_offset):
		byte_count += 1
		if byte_count >= len(data):
			return -1
	return byte_count


def show_bytes(data: bytes, offset: int, pattern: str):
	"""Show hex bytes around pattern"""
	start = max(0, offset - 32)
	end = min(len(data), offset + len(pattern) + 32)

	print(f"\n        Hex context:")
	for i in range(start, end, 16):
		chunk = data[i:i+16]
		hex_part = ' '.join(f'{b:02x}' for b in chunk)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
		marker = " >>>" if i <= offset < i + 16 else "    "
		print(f"        {marker} {i:08x}: {hex_part:48s} {ascii_part}")
	print()


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')
	analyze_structure(decompressed_file)
