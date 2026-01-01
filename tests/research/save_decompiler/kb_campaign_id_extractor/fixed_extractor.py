"""
Fixed character name extraction with proper UTF-16LE parsing.
"""
from pathlib import Path
import struct
import zlib
import hashlib
import json


def decompress_save_file(save_path: Path) -> bytes:
	"""Decompress King's Bounty save data file."""
	with open(save_path, 'rb') as f:
		data = f.read()

	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	compressed_data = data[12:12+compressed_size]
	return zlib.decompress(compressed_data)


def extract_utf16_string_at(data: bytes, offset: int, max_length: int = 100) -> str:
	"""
	Extract UTF-16LE string starting at offset.

	Reads until null terminator or non-printable character.
	"""
	string_bytes = bytearray()
	i = offset

	while i < min(offset + max_length * 2, len(data) - 1):
		b1 = data[i]
		b2 = data[i + 1]

		# Check for null terminator
		if b1 == 0 and b2 == 0:
			break

		# Check for valid UTF-16LE character (Cyrillic or Latin)
		if (b2 == 0x04) or (b2 == 0x00 and 0x20 <= b1 <= 0x7E):
			string_bytes.append(b1)
			string_bytes.append(b2)
			i += 2
		else:
			break

	if string_bytes:
		try:
			return bytes(string_bytes).decode('utf-16-le')
		except:
			return ""

	return ""


def find_character_names(data: bytes) -> dict[str, str]:
	"""
	Find character names in decompressed save data.

	Strategy: Scan first 100KB for UTF-16LE Cyrillic strings.
	Character names appear early in file.
	"""
	names = []

	# Scan first 100KB
	search_limit = min(100000, len(data))

	i = 0
	while i < search_limit - 4:
		byte1 = data[i]
		byte2 = data[i + 1]

		# Check for start of Cyrillic UTF-16LE string
		if byte2 == 0x04 and 0x10 <= byte1 <= 0x4F:  # Cyrillic range
			string = extract_utf16_string_at(data, i)

			if string and len(string) >= 4:  # At least 4 characters
				# Filter out common non-name strings
				if not any(skip in string.lower() for skip in [
					'crap', 'flags', 'clouds', 'hero', 'nickname',
					'arena', 'enemy', 'player', 'shop', 'item'
				]):
					names.append({
						'offset': i,
						'string': string,
						'length': len(string)
					})

			i += len(string.encode('utf-16-le')) if string else 2
		else:
			i += 1

	# Character names are typically:
	# - Between 4-20 characters
	# - Appear in first 30KB
	# - Are unique (not repeated many times)

	candidate_names = []
	for name_info in names:
		if (4 <= name_info['length'] <= 20 and
			name_info['offset'] < 30000):
			candidate_names.append(name_info)

	# Return first 2-3 unique candidate names as likely character names
	unique_names = []
	seen = set()

	for name_info in candidate_names:
		if name_info['string'] not in seen:
			unique_names.append(name_info['string'])
			seen.add(name_info['string'])

		if len(unique_names) >= 3:
			break

	return {
		'name1': unique_names[0] if len(unique_names) > 0 else '',
		'name2': unique_names[1] if len(unique_names) > 1 else '',
		'name3': unique_names[2] if len(unique_names) > 2 else '',
	}


def compute_campaign_id(names: dict) -> str:
	"""
	Compute campaign ID from hero names only.

	Note: name1 is usually pet name, so we skip it.
	Hero has only first name (name2) and second name (name3).
	"""
	combined = f"{names.get('name2', '')}|{names.get('name3', '')}"
	return hashlib.md5(combined.encode('utf-8')).hexdigest()


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
	print("FIXED CHARACTER NAME EXTRACTION")
	print("=" * 80)

	results = {}

	for save_id, path in saves.items():
		print(f"\n{save_id}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)
		names = find_character_names(data)
		campaign_id = compute_campaign_id(names)

		results[save_id] = {
			'names': names,
			'campaign_id': campaign_id
		}

		print(f"  Pet Name: {names['name1']}")
		print(f"  Hero First Name: {names['name2']}")
		print(f"  Hero Second Name: {names['name3']}")
		print(f"  Campaign ID (from hero names): {campaign_id}")

	# Validation
	print("\n" + "=" * 80)
	print("VALIDATION")
	print("=" * 80)

	c1s1_id = results['C1S1']['campaign_id']
	c1s2_id = results['C1S2']['campaign_id']
	c2s1_id = results['C2S1']['campaign_id']
	c2s2_id = results['C2S2']['campaign_id']

	print(f"\n  Campaign 1 Save 1: {c1s1_id}")
	print(f"  Campaign 1 Save 2: {c1s2_id}")
	print(f"  Campaign 2 Save 1: {c2s1_id}")
	print(f"  Campaign 2 Save 2: {c2s2_id}")

	c1_match = (c1s1_id == c1s2_id)
	c2_match = (c2s1_id == c2s2_id)
	campaigns_differ = (c1s1_id != c2s1_id)

	print(f"\n  Campaign 1 saves match: {c1_match}")
	print(f"  Campaign 2 saves match: {c2_match}")
	print(f"  Campaigns differ: {campaigns_differ}")

	if c1_match and c2_match and campaigns_differ:
		print("\n" + "=" * 80)
		print("SUCCESS! Campaign identification works!")
		print("=" * 80)

		c1_names = results['C1S1']['names']
		c2_names = results['C2S1']['names']

		print(f"\n  Campaign 1 Hero: {c1_names['name2']} {c1_names['name3']}")
		print(f"  Campaign 1 ID: {c1s1_id}")

		print(f"\n  Campaign 2 Hero: {c2_names['name2']} {c2_names['name3']}")
		print(f"  Campaign 2 ID: {c2s1_id}")

	# Save results
	output_file = Path('tmp/fixed_campaign_ids.json')
	output_file.parent.mkdir(exist_ok=True)

	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(results, f, ensure_ascii=False, indent=2)

	print(f"\n  Results saved to: {output_file}")


if __name__ == '__main__':
	main()
