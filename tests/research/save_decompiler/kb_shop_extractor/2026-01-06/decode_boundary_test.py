#!/usr/bin/env python3
"""
Test what happens when UTF-16-LE decoding occurs across chunk boundaries.
Simulates the exact behavior of _find_all_shop_ids method.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def simulate_chunked_parsing(data: bytes, chunk_size: int = 10000):
	"""Simulate the chunked parsing exactly as done in _find_all_shop_ids"""
	shops = []
	pos = 0

	print(f"Total data size: {len(data)} bytes")
	print(f"Chunk size: {chunk_size} bytes")
	print("=" * 80)

	while pos < len(data):
		current_chunk_size = chunk_size
		if pos + chunk_size > len(data):
			current_chunk_size = len(data) - pos

		chunk_start = pos
		chunk_end = pos + current_chunk_size

		print(f"\nProcessing chunk: {chunk_start} - {chunk_end}")

		try:
			# Exact same decoding as in the original code
			text = data[pos:pos+current_chunk_size].decode('utf-16-le', errors='ignore')

			# Find all matches using the same regex
			matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

			for match in matches:
				shop_id_full = match.group(0)
				location = match.group(1)
				shop_num = match.group(2)
				shop_id = location + '_' + shop_num

				# Only show shops matching our target
				if 'm_zcom_start' in shop_id:
					shop_bytes = shop_id_full.encode('utf-16-le')
					actual_pos = data.find(shop_bytes, pos, pos+current_chunk_size)

					print(f"  Found match: {shop_id_full}")
					print(f"    Location: {location}")
					print(f"    Shop num: {shop_num}")
					print(f"    Reconstructed ID: {shop_id}")
					print(f"    Match position in text: {match.start()} (char offset)")
					print(f"    Byte position search result: {actual_pos}")

					if actual_pos != -1:
						# Check if this is a duplicate
						is_duplicate = shop_id in [s[0] for s in shops]
						print(f"    Is duplicate: {is_duplicate}")

						if not is_duplicate:
							shops.append((shop_id, actual_pos))
							print(f"    ADDED to shops list")
						else:
							print(f"    SKIPPED (duplicate)")
					else:
						print(f"    NOT FOUND in binary search - SKIPPED")

		except Exception as e:
			print(f"  Error: {e}")

		pos += chunk_size

	print("\n" + "=" * 80)
	print("FINAL RESULTS:")
	print("=" * 80)

	for shop_id, shop_pos in shops:
		if 'm_zcom_start' in shop_id:
			print(f"  {shop_id} at position {shop_pos}")

	return shops


def inspect_boundary_region(data: bytes, position: int, window: int = 100):
	"""Inspect the data around a specific position"""
	start = max(0, position - window)
	end = min(len(data), position + window)

	print(f"\nInspecting region around position {position}:")
	print(f"Range: {start} - {end}")
	print("-" * 80)

	# Show hex dump
	chunk = data[start:end]
	print("Hex dump:")
	for i in range(0, len(chunk), 32):
		hex_part = ' '.join(f'{b:02x}' for b in chunk[i:i+32])
		print(f"  {start + i:08x}: {hex_part}")

	# Try to decode
	try:
		decoded = chunk.decode('utf-16-le', errors='replace')
		print(f"\nDecoded text:")
		print(f"  {repr(decoded)}")
	except Exception as e:
		print(f"\nDecoding failed: {e}")


def main():
	decompressor = SaveFileDecompressor()
	quicksave_path = Path('/saves/Darkside/quick1767649866/data')

	print("=" * 80)
	print("SIMULATING CHUNKED PARSING - QUICKSAVE")
	print("=" * 80)

	data = decompressor.decompress(quicksave_path)

	# Simulate the exact parsing behavior
	shops = simulate_chunked_parsing(data, chunk_size=10000)

	# Inspect the boundary region where occurrence #5 appears
	# Position 529960, chunk ends at 530000, so 40 bytes before end
	print("\n" + "=" * 80)
	print("INSPECTING CHUNK BOUNDARY AT POSITION 529960")
	print("=" * 80)

	inspect_boundary_region(data, 529960, window=150)

	# Also inspect where the chunk boundary is
	print("\n" + "=" * 80)
	print("INSPECTING CHUNK BOUNDARY AT POSITION 530000 (chunk end)")
	print("=" * 80)

	inspect_boundary_region(data, 530000, window=150)


if __name__ == '__main__':
	main()
