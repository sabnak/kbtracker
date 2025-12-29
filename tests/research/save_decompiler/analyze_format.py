#!/usr/bin/env python3
"""
Analyze King's Bounty save file format
"""
import struct
import zlib


def analyze_header(file_path: str):
	"""Analyze save file header structure"""
	with open(file_path, 'rb') as f:
		# Read first 256 bytes
		header = f.read(256)

		print("=== Save File Header Analysis ===\n")

		# Magic header (4 bytes)
		magic = header[0:4].decode('ascii')
		print(f"Magic: '{magic}'")

		# Next 8 bytes might be size values
		val1 = struct.unpack('<I', header[4:8])[0]
		val2 = struct.unpack('<I', header[8:12])[0]
		print(f"Value 1 (offset 4): {val1} (0x{val1:08x})")
		print(f"Value 2 (offset 8): {val2} (0x{val2:08x})")

		# Check for zlib header at offset 12
		if header[12:14] == b'\x78\x01':
			print("\n[+] ZLIB compression detected at offset 12!")
			print("    Header bytes: 78 01 (default compression)")
			return 12
		elif header[12:14] == b'\x78\x9c':
			print("\n[+] ZLIB compression detected at offset 12!")
			print("    Header bytes: 78 9c (best compression)")
			return 12
		else:
			print(f"\nChecking for zlib header...")
			print(f"  Bytes at offset 12: {header[12:14].hex()}")

			# Search for zlib header
			for i in range(256):
				if header[i:i+2] in [b'\x78\x01', b'\x78\x9c', b'\x78\xda']:
					print(f"  Found potential zlib header at offset {i}")
					return i

		return None


def test_decompression(file_path: str, offset: int):
	"""Try to decompress data starting at offset"""
	print(f"\n=== Testing Decompression (offset {offset}) ===\n")

	with open(file_path, 'rb') as f:
		f.seek(offset)
		compressed_data = f.read()

		try:
			decompressed = zlib.decompress(compressed_data)
			print(f"[+] SUCCESS! Decompressed {len(compressed_data)} bytes -> {len(decompressed)} bytes")
			print(f"    Compression ratio: {len(decompressed) / len(compressed_data):.2f}x")
			return decompressed
		except zlib.error as e:
			print(f"[-] FAILED: {e}")
			return None


def preview_decompressed(data: bytes, num_bytes: int = 512):
	"""Show preview of decompressed data"""
	print(f"\n=== Decompressed Data Preview (first {num_bytes} bytes) ===\n")

	# Hex dump
	for i in range(0, min(num_bytes, len(data)), 16):
		hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
		print(f"{i:08x}: {hex_part:48s} {ascii_part}")

	print()


def search_strings(data: bytes, min_length: int = 10):
	"""Extract readable ASCII strings from binary data"""
	print(f"\n=== Searching for Strings (min length {min_length}) ===\n")

	strings = []
	current = []

	for byte in data[:10000]:  # Search first 10KB
		if 32 <= byte < 127:  # Printable ASCII
			current.append(chr(byte))
		else:
			if len(current) >= min_length:
				strings.append(''.join(current))
			current = []

	# Print first 20 strings
	for i, s in enumerate(strings[:20]):
		print(f"  {i+1}. '{s}'")

	print(f"\nFound {len(strings)} strings total")
	return strings


if __name__ == '__main__':
	save_file = r'F:\var\kbtracker\tests\game_files\saves\1707078232\data'

	# Analyze header
	zlib_offset = analyze_header(save_file)

	if zlib_offset is not None:
		# Try decompression
		decompressed = test_decompression(save_file, zlib_offset)

		if decompressed:
			# Preview data
			preview_decompressed(decompressed)

			# Search for strings
			search_strings(decompressed)

			# Save decompressed data
			import os
			script_dir = os.path.dirname(os.path.abspath(__file__))
			output_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')
			with open(output_file, 'wb') as f:
				f.write(decompressed)
			print(f"\n[+] Saved decompressed data to: tmp/decompressed.bin")
