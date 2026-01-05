#!/usr/bin/env python3
"""
Decompress new save file 1767209722
"""
import struct
import zlib
import os


def decompress_save(input_file: str, output_file: str) -> None:
	"""Decompress King's Bounty save file"""
	with open(input_file, 'rb') as f:
		# Read header
		magic = f.read(4)
		print(f"Magic: {magic}")

		# Read sizes
		compressed_size = struct.unpack('<I', f.read(4))[0]
		decompressed_size = struct.unpack('<I', f.read(4))[0]

		print(f"Compressed size:   {compressed_size:,} bytes")
		print(f"Decompressed size: {decompressed_size:,} bytes")

		# Read compressed data
		compressed_data = f.read()
		print(f"Read {len(compressed_data):,} bytes of compressed data")

		# Decompress
		decompressed = zlib.decompress(compressed_data)
		print(f"Decompressed to {len(decompressed):,} bytes")

		# Write output
		with open(output_file, 'wb') as out:
			out.write(decompressed)

		print(f"\n[SUCCESS] Saved to: {output_file}")


if __name__ == '__main__':
	saves_dir = r'/tests/game_files/saves/1767209722'
	input_file = os.path.join(saves_dir, 'data')
	output_file = r'/tests/research/save_decompiler/kb_shop_extractor/tmp\decompressed_new.bin'

	print("="*78)
	print("DECOMPRESSING NEW SAVE FILE (1767209722)")
	print("="*78)
	print()

	decompress_save(input_file, output_file)
