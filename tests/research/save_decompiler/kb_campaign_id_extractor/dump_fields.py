"""
Dump all ASCII strings (potential field names) from the start of decompressed data.
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


def extract_strings(data: bytes, min_length: int = 3) -> list[tuple[int, str]]:
	"""Extract printable ASCII strings from binary data."""
	strings = []
	# Match sequences of word characters (letters, numbers, underscores)
	pattern_str = b'[a-zA-Z_][a-zA-Z0-9_]{3,50}'
	pattern = re.compile(pattern_str)

	for match in pattern.finditer(data):
		try:
			string = match.group().decode('utf-8')
			strings.append((match.start(), string))
		except:
			pass

	return strings


def main():
	"""Main function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'data',
		'C1S2': saves_dir / '1707047253' / 'data',
		'C2S1': saves_dir / '1766864874' / 'data',
		'C2S2': saves_dir / '1767209722' / 'data',
	}

	print("=" * 80)
	print("EXTRACTING FIELD NAMES FROM DECOMPRESSED DATA")
	print("=" * 80)

	all_strings = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)
		strings = extract_strings(data[:50000], min_length=4)

		all_strings[name] = strings

		print(f"  Found {len(strings)} strings in first 50KB")
		print(f"\n  First 100 strings:")

		for i, (offset, string) in enumerate(strings[:100]):
			print(f"    0x{offset:06x}  {string}")

	# Find strings that exist in all 4 files
	print("\n" + "=" * 80)
	print("STRINGS PRESENT IN ALL 4 SAVES")
	print("=" * 80)

	# Get unique strings from each save
	sets = {name: set(s for _, s in strings) for name, strings in all_strings.items()}

	# Find intersection
	common_strings = sets['C1S1'] & sets['C1S2'] & sets['C2S1'] & sets['C2S2']

	print(f"\nFound {len(common_strings)} common strings")
	for i, string in enumerate(sorted(common_strings)[:200]):
		print(f"  {string}")

	# Find strings unique to Campaign 1
	print("\n" + "=" * 80)
	print("STRINGS UNIQUE TO CAMPAIGN 1 (in both C1 saves but not C2)")
	print("=" * 80)

	c1_unique = (sets['C1S1'] & sets['C1S2']) - (sets['C2S1'] | sets['C2S2'])

	print(f"\nFound {len(c1_unique)} Campaign 1 unique strings")
	for i, string in enumerate(sorted(c1_unique)[:50]):
		print(f"  {string}")

	# Find strings unique to Campaign 2
	print("\n" + "=" * 80)
	print("STRINGS UNIQUE TO CAMPAIGN 2 (in both C2 saves but not C1)")
	print("=" * 80)

	c2_unique = (sets['C2S1'] & sets['C2S2']) - (sets['C1S1'] | sets['C1S2'])

	print(f"\nFound {len(c2_unique)} Campaign 2 unique strings")
	for i, string in enumerate(sorted(c2_unique)[:50]):
		print(f"  {string}")


if __name__ == '__main__':
	main()
