"""
Search for specific character names in save files to verify extraction.
"""
from pathlib import Path
import struct
import zlib
import re


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	return zlib.decompress(compressed_data)


def search_for_string(data: bytes, search_str: str) -> list[int]:
	"""Search for UTF-16LE encoded string in data."""
	search_bytes = search_str.encode('utf-16-le')

	offsets = []
	offset = 0

	while True:
		pos = data.find(search_bytes, offset)
		if pos == -1:
			break
		offsets.append(pos)
		offset = pos + 1

	return offsets


def extract_all_utf16_strings(data: bytes, min_length: int = 4, max_offset: int = 50000) -> list[tuple[int, str]]:
	"""
	Extract all UTF-16LE strings from data.

	Returns: [(offset, string), ...]
	"""
	strings = []

	i = 0
	while i < max_offset - 4:
		# Check if this looks like start of UTF-16LE string
		# Could be Cyrillic (0x04XX) or Latin (0x00XX)
		byte1 = data[i]
		byte2 = data[i + 1]

		# Check for UTF-16LE pattern
		if byte2 == 0x04 or (byte2 == 0x00 and 0x20 <= byte1 <= 0x7E):
			# Try to read string
			string_bytes = bytearray()
			j = i

			while j < min(i + 200, len(data) - 1):
				b1 = data[j]
				b2 = data[j + 1]

				# Cyrillic or basic Latin
				if (b2 == 0x04) or (b2 == 0x00 and (0x20 <= b1 <= 0x7E or b1 == 0)):
					if b1 == 0 and b2 == 0:  # Null terminator
						break
					string_bytes.append(b1)
					string_bytes.append(b2)
					j += 2
				else:
					break

			if len(string_bytes) >= min_length * 2:  # At least min_length characters
				try:
					decoded = bytes(string_bytes).decode('utf-16-le')
					if decoded and decoded.strip():
						strings.append((i, decoded))
						i = j  # Skip past this string
						continue
				except:
					pass

		i += 1

	return strings


def main():
	"""Main function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	# Expected names from user
	expected = {
		'C1': ['Неолина', 'Очаровательная'],
		'C2': ['Даэрт', 'дэ Мортон'],
	}

	saves = {
		'C1S1': saves_dir / '1707078232' / 'data',
		'C1S2': saves_dir / '1707047253' / 'data',
		'C2S1': saves_dir / '1766864874' / 'data',
		'C2S2': saves_dir / '1767209722' / 'data',
	}

	print("=" * 80)
	print("SEARCHING FOR EXPECTED CHARACTER NAMES")
	print("=" * 80)

	for name, path in saves.items():
		campaign = name[:2]
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)

		# Search for expected names
		for expected_name in expected[campaign]:
			offsets = search_for_string(data, expected_name)
			if offsets:
				print(f"  Found '{expected_name}' at {len(offsets)} location(s):")
				for offset in offsets[:3]:
					print(f"    Offset 0x{offset:08x} ({offset})")
			else:
				print(f"  NOT FOUND: '{expected_name}'")

	# Extract ALL strings to see what's there
	print("\n" + "=" * 80)
	print("EXTRACTING ALL UTF-16LE STRINGS (first 20 per save)")
	print("=" * 80)

	for name, path in saves.items():
		print(f"\n{name}:")
		print("-" * 80)

		data = decompress_save_file(path)
		strings = extract_all_utf16_strings(data, min_length=4, max_offset=20000)

		# Show first 20 strings
		for i, (offset, string) in enumerate(strings[:20]):
			print(f"  0x{offset:06x}: '{string}'")


if __name__ == '__main__':
	main()
