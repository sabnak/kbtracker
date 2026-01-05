#!/usr/bin/env python3
"""
Script to analyze shop ID parsing in save files.
Compares how shop IDs appear in binary data vs how they're parsed.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def find_shop_id_occurrences(data: bytes, shop_prefix: str) -> list:
	"""Find all occurrences of a shop ID in binary data"""
	results = []

	# Search for the shop ID pattern in UTF-16-LE encoded form
	# We'll search for itext_m_zcom_start_ and see what follows
	search_pattern = f'itext_{shop_prefix}_'.encode('utf-16-le')

	pos = 0
	while True:
		pos = data.find(search_pattern, pos)
		if pos == -1:
			break

		# Read the next 40 bytes to see what follows
		end_pos = min(pos + len(search_pattern) + 40, len(data))
		surrounding = data[pos:end_pos]

		try:
			decoded = surrounding.decode('utf-16-le', errors='ignore')
			results.append({
				'position': pos,
				'hex_offset': hex(pos),
				'surrounding_text': decoded,
				'raw_bytes': surrounding.hex()
			})
		except:
			pass

		pos += 1

	return results


def analyze_chunk_boundaries(data: bytes, shop_prefix: str):
	"""Analyze how shop IDs fall across chunk boundaries"""
	search_pattern = f'itext_{shop_prefix}_'.encode('utf-16-le')

	chunk_size = 10000
	occurrences = []

	pos = 0
	while pos < len(data):
		chunk_end = min(pos + chunk_size, len(data))

		# Find occurrences in this chunk
		chunk_data = data[pos:chunk_end]
		chunk_pos = 0

		while True:
			found = chunk_data.find(search_pattern, chunk_pos)
			if found == -1:
				break

			absolute_pos = pos + found

			# Check if this falls near a chunk boundary
			distance_from_end = chunk_end - absolute_pos

			# Read what follows the pattern
			try:
				# Read 30 bytes after the pattern
				read_end = min(absolute_pos + len(search_pattern) + 30, len(data))
				following = data[absolute_pos + len(search_pattern):read_end]
				decoded_following = following.decode('utf-16-le', errors='ignore')

				occurrences.append({
					'absolute_position': absolute_pos,
					'chunk_start': pos,
					'chunk_end': chunk_end,
					'distance_from_chunk_end': distance_from_end,
					'decoded_following': decoded_following,
					'near_boundary': distance_from_end < 100
				})
			except:
				pass

			chunk_pos = found + 1

		pos += chunk_size

	return occurrences


def main():
	decompressor = SaveFileDecompressor()

	quicksave_path = Path('/saves/Darkside/quick1767649866/data')
	manual_save_path = Path('/saves/Darkside/1767650305/data')

	print("=" * 80)
	print("SHOP ID ANALYSIS: m_zcom_start")
	print("=" * 80)

	for save_name, save_path in [
		("QUICKSAVE", quicksave_path),
		("MANUAL SAVE", manual_save_path)
	]:
		print(f"\n{save_name}: {save_path}")
		print("-" * 80)

		data = decompressor.decompress(save_path)

		# Find all occurrences
		occurrences = find_shop_id_occurrences(data, 'm_zcom_start')
		print(f"\nFound {len(occurrences)} occurrence(s) of 'itext_m_zcom_start_':\n")

		for i, occ in enumerate(occurrences, 1):
			print(f"Occurrence #{i}:")
			print(f"  Position: {occ['position']} ({occ['hex_offset']})")
			print(f"  Decoded text: {repr(occ['surrounding_text'])}")
			print()

		# Analyze chunk boundaries
		print("\nChunk Boundary Analysis:")
		print("-" * 80)

		chunk_analysis = analyze_chunk_boundaries(data, 'm_zcom_start')

		for i, occ in enumerate(chunk_analysis, 1):
			print(f"Occurrence #{i}:")
			print(f"  Absolute position: {occ['absolute_position']}")
			print(f"  Chunk range: {occ['chunk_start']} - {occ['chunk_end']}")
			print(f"  Distance from chunk end: {occ['distance_from_chunk_end']} bytes")
			print(f"  Near boundary: {occ['near_boundary']}")
			print(f"  Following text: {repr(occ['decoded_following'][:50])}")
			print()

	print("\n" + "=" * 80)
	print("REGEX PATTERN TESTING")
	print("=" * 80)

	# Test the regex pattern on sample strings
	test_strings = [
		"itext_m_zcom_start_519",
		"itext_m_zcom_start_5",
		"text_m_zcom_start_519abc",
		"itext_m_zcom_start_51",
		"itext_m_zcom_start_5\x00",
		"itext_m_zcom_start_519\x00",
	]

	pattern = re.compile(r'itext_([-\w]+)_(\d+)')

	for test in test_strings:
		match = pattern.search(test)
		if match:
			print(f"Input: {repr(test)}")
			print(f"  Full match: {repr(match.group(0))}")
			print(f"  Location: {repr(match.group(1))}")
			print(f"  Shop num: {repr(match.group(2))}")
			print(f"  Reconstructed: {match.group(1)}_{match.group(2)}")
			print()


if __name__ == '__main__':
	main()
