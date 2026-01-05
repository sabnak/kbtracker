#!/usr/bin/env python3
"""
Demonstrate the UTF-16-LE alignment issue at chunk boundaries.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def main():
	decompressor = SaveFileDecompressor()
	quicksave_path = Path('/saves/Darkside/quick1767649866/data')
	data = decompressor.decompress(quicksave_path)

	# The chunk boundary that causes the issue
	chunk_start = 520000
	chunk_end = 530000

	print("=" * 80)
	print("UTF-16-LE ALIGNMENT ISSUE DEMONSTRATION")
	print("=" * 80)

	# Extract the exact chunk that causes the problem
	chunk = data[chunk_start:chunk_end]

	print(f"\nChunk range: {chunk_start} - {chunk_end}")
	print(f"Chunk size: {len(chunk)} bytes")
	print(f"Chunk size is odd: {len(chunk) % 2 == 1}")

	# Decode the chunk
	text = chunk.decode('utf-16-le', errors='ignore')
	print(f"\nDecoded text length: {len(text)} characters")

	# Find matches
	matches = list(re.finditer(r'itext_([-\w]+)_(\d+)', text))
	print(f"\nTotal regex matches in chunk: {len(matches)}")

	# Show all matches containing m_zcom_start
	print("\nMatches containing 'm_zcom_start':")
	for i, match in enumerate(matches, 1):
		if 'm_zcom_start' in match.group(0):
			print(f"\n  Match #{i}:")
			print(f"    Full match: {repr(match.group(0))}")
			print(f"    Location: {match.group(1)}")
			print(f"    Shop num: {match.group(2)}")
			print(f"    Char position in decoded text: {match.start()}")

			# Calculate byte position in chunk
			chars_before = text[:match.start()]
			approx_byte_pos = len(chars_before.encode('utf-16-le'))
			absolute_byte_pos = chunk_start + approx_byte_pos

			print(f"    Approximate byte position in chunk: {approx_byte_pos}")
			print(f"    Approximate absolute position: {absolute_byte_pos}")

			# Show context around the match
			context_start = max(0, match.start() - 10)
			context_end = min(len(text), match.end() + 10)
			context = text[context_start:context_end]
			print(f"    Context: {repr(context)}")

	# Now show what happens at the exact byte boundary
	print("\n" + "=" * 80)
	print("ANALYSIS OF CHUNK BOUNDARY")
	print("=" * 80)

	# Find where "itext_m_zcom_start_519" actually is in the binary
	search_pattern = b'i\x00t\x00e\x00x\x00t\x00_\x00m\x00_\x00z\x00c\x00o\x00m\x00_\x00s\x00t\x00a\x00r\x00t\x00_\x005\x001\x009\x00'
	pos = data.find(search_pattern, chunk_start, chunk_end + 200)

	if pos != -1:
		print(f"\nFound 'itext_m_zcom_start_519' at byte position: {pos}")
		print(f"Chunk ends at: {chunk_end}")
		print(f"Distance from chunk end: {chunk_end - pos} bytes")

		# Show what bytes are at the boundary
		boundary_region = data[chunk_end - 20:chunk_end + 20]
		print(f"\nBytes around chunk boundary ({chunk_end - 20} to {chunk_end + 20}):")
		for i in range(0, len(boundary_region), 20):
			offset = chunk_end - 20 + i
			hex_bytes = ' '.join(f'{b:02x}' for b in boundary_region[i:i+20])
			print(f"  {offset:08x}: {hex_bytes}")

		# Show what happens when we decode across the boundary
		print(f"\n--- Decoding chunk BEFORE boundary (last 60 bytes) ---")
		before_boundary = chunk[-60:]
		try:
			decoded_before = before_boundary.decode('utf-16-le', errors='ignore')
			print(f"Decoded: {repr(decoded_before)}")
		except Exception as e:
			print(f"Error: {e}")

		print(f"\n--- Decoding chunk AFTER boundary (first 60 bytes) ---")
		after_boundary = data[chunk_end:chunk_end + 60]
		try:
			decoded_after = after_boundary.decode('utf-16-le', errors='ignore')
			print(f"Decoded: {repr(decoded_after)}")
		except Exception as e:
			print(f"Error: {e}")

	# Check if the chunk size is aligned to UTF-16 (should be even)
	print("\n" + "=" * 80)
	print("ROOT CAUSE ANALYSIS")
	print("=" * 80)

	print(f"\nChunk size: {chunk_end - chunk_start} bytes")
	print(f"Is chunk size even (UTF-16 aligned): {(chunk_end - chunk_start) % 2 == 0}")
	print(f"Chunk start position: {chunk_start}")
	print(f"Is chunk start even (UTF-16 aligned): {chunk_start % 2 == 0}")

	print("\nConclusion:")
	if chunk_start % 2 == 0:
		print("  Chunk starts on even boundary (GOOD for UTF-16-LE)")
	else:
		print("  WARNING: Chunk starts on ODD boundary (BAD for UTF-16-LE)")

	print("""
UTF-16-LE encoding uses 2 bytes per character. When we decode a chunk with
'errors=ignore', characters that are split across the boundary will be
corrupted or interpreted differently.

In this case, when decoding the chunk from 520000-530000:
- The string 'itext_m_zcom_start_519_terr' is near the end of the chunk
- Due to malformed UTF-16 at the boundary, the decoder might produce
  corrupted output that causes the regex to match 'itext_m_zcom_start_5'
  instead of the full '519'
""")


if __name__ == '__main__':
	main()
