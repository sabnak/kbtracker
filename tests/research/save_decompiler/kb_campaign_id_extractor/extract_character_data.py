"""
Extract character data (name, class, emblem) from save files.
This will be used as a composite campaign identifier.
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


def extract_field_value(data: bytes, field_name: str, search_limit: int = 100000) -> list[str]:
	"""
	Extract value(s) following a field name.

	Looks for UTF-16LE encoded strings near the field name.
	"""
	results = []
	field_bytes = field_name.encode('utf-8')

	offset = 0
	while offset < search_limit:
		pos = data.find(field_bytes, offset)
		if pos == -1:
			break

		# Try to find UTF-16LE string after field name
		search_start = pos + len(field_bytes)
		search_end = min(search_start + 200, len(data))

		# Look for Cyrillic UTF-16LE patterns (Russian characters)
		# Cyrillic in UTF-16LE: 0x0400-0x04FF range
		for i in range(search_start, search_end - 4, 2):
			# Check if this looks like UTF-16LE Cyrillic
			byte1 = data[i]
			byte2 = data[i + 1]

			# UTF-16LE Cyrillic character check
			if byte2 == 0x04 and 0x00 <= byte1 <= 0xFF:
				# Found potential start of Cyrillic string
				string_data = bytearray()
				j = i

				# Read until we hit non-Cyrillic or null
				while j < search_end - 1:
					b1 = data[j]
					b2 = data[j + 1]

					# Cyrillic range or common punctuation
					if (b2 == 0x04 and 0x00 <= b1 <= 0xFF) or (b2 == 0x00 and 0x20 <= b1 <= 0x7E):
						string_data.append(b1)
						string_data.append(b2)
						j += 2
					else:
						break

				if len(string_data) >= 4:  # At least 2 characters
					try:
						decoded = bytes(string_data).decode('utf-16-le')
						if decoded and decoded.isprintable():
							results.append(decoded)
							break
					except:
						pass

		offset = pos + 1

	return results


def find_hero_class(data: bytes, search_limit: int = 100000) -> list[str]:
	"""
	Find hero class/race.

	Common classes: orc, vampire, demoness, etc.
	"""
	classes = []

	# Search for class-like strings
	class_patterns = [
		b'orc', b'vampire', b'demoness', b'warrior',
		# Russian equivalents
		'орк', 'вампир', 'демонесса',
	]

	for pattern in class_patterns:
		if isinstance(pattern, str):
			pattern_bytes = pattern.encode('utf-16-le')
		else:
			pattern_bytes = pattern

		if pattern_bytes in data[:search_limit]:
			if isinstance(pattern, str):
				classes.append(pattern)
			else:
				classes.append(pattern.decode('utf-8'))

	return classes


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
	print("EXTRACTING CHARACTER DATA FROM SAVES")
	print("=" * 80)

	character_data = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)

		# Search for hero name fields
		hero_names = extract_field_value(data, 'hero')
		nicknames = extract_field_value(data, 'nickname')
		pn_values = extract_field_value(data, 'pn')  # Might be first/last name
		hernm_values = extract_field_value(data, 'hernm')

		# Search for class
		classes = find_hero_class(data)

		character_data[name] = {
			'hero': hero_names,
			'nickname': nicknames,
			'pn': pn_values,
			'hernm': hernm_values,
			'class': classes,
		}

		print(f"\n  Hero names found: {hero_names}")
		print(f"  Nicknames found: {nicknames}")
		print(f"  'pn' values found: {pn_values}")
		print(f"  'hernm' values found: {hernm_values}")
		print(f"  Classes found: {classes}")

	# Compare between campaigns
	print("\n" + "=" * 80)
	print("CAMPAIGN COMPARISON")
	print("=" * 80)

	print("\nCampaign 1:")
	print(f"  C1S1: {character_data['C1S1']}")
	print(f"  C1S2: {character_data['C1S2']}")

	print("\nCampaign 2:")
	print(f"  C2S1: {character_data['C2S1']}")
	print(f"  C2S2: {character_data['C2S2']}")

	# Check if character data is same within campaigns
	if character_data['C1S1'] and character_data['C1S2']:
		c1_same = (character_data['C1S1'] == character_data['C1S2'])
		print(f"\n  Campaign 1 character data matches: {c1_same}")

	if character_data['C2S1'] and character_data['C2S2']:
		c2_same = (character_data['C2S1'] == character_data['C2S2'])
		print(f"  Campaign 2 character data matches: {c2_same}")


if __name__ == '__main__':
	main()
