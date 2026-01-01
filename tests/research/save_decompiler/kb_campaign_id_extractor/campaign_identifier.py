"""
Extract composite campaign identifier from save files.

Identifier = Hash(FirstName + SecondName + Race + Emblem)
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


def find_string_after_marker(data: bytes, marker: bytes, max_distance: int = 200) -> str:
	"""Find UTF-16LE string after a marker."""
	pos = data.find(marker)
	if pos == -1:
		return ""

	# Search for UTF-16LE string after marker
	search_start = pos + len(marker)
	search_end = min(search_start + max_distance, len(data))

	# Try to find string starting with length prefix
	for i in range(search_start, search_end - 4):
		# Check for potential UTF-16LE string
		# Look for pattern: [length as uint32] [utf-16le data]
		if i + 4 <= len(data):
			potential_length = struct.unpack('<I', data[i:i+4])[0]

			# Reasonable string length (1-100 chars = 2-200 bytes)
			if 1 <= potential_length <= 200:
				string_start = i + 4
				string_end = string_start + potential_length

				if string_end <= len(data):
					try:
						string_bytes = data[string_start:string_end]
						decoded = string_bytes.decode('utf-16-le')

						# Check if it's printable
						if decoded and all(c.isprintable() or c in '\n\r\t' for c in decoded):
							return decoded.strip('\x00')
					except:
						pass

	return ""


def extract_character_info(data: bytes) -> dict[str, str]:
	"""Extract character information from decompressed save data."""
	info = {}

	# Find 'pn' field (first name)
	first_name = find_string_after_marker(data, b'pn')
	info['first_name'] = first_name

	# Find 'nickname' field (second name / epithet)
	nickname = find_string_after_marker(data, b'nickname')
	info['nickname'] = nickname

	# Find hero name
	hero = find_string_after_marker(data, b'hero')
	info['hero'] = hero

	# Try to find race/class
	# Common races in UTF-16LE
	races = {
		'orc': 'орк',
		'vampire': 'вампир',
		'demoness': 'демонесса',
	}

	race_found = ""
	for eng, rus in races.items():
		rus_bytes = rus.encode('utf-16-le')
		if rus_bytes in data[:50000]:  # Search first 50KB
			race_found = eng
			break

	info['race'] = race_found

	return info


def compute_campaign_id(character_info: dict[str, str]) -> str:
	"""
	Compute campaign ID from character info.

	Uses MD5 hash of combined fields.
	"""
	# Combine all fields
	combined = (
		character_info.get('first_name', '') +
		'|' +
		character_info.get('nickname', '') +
		'|' +
		character_info.get('hero', '') +
		'|' +
		character_info.get('race', '')
	)

	# Compute hash
	hash_obj = hashlib.md5(combined.encode('utf-8'))
	campaign_id = hash_obj.hexdigest()

	return campaign_id


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
	print("CAMPAIGN IDENTIFIER EXTRACTION")
	print("=" * 80)

	results = {}

	for name, path in saves.items():
		print(f"\n{name}: {path.parent.name}")
		print("-" * 80)

		data = decompress_save_file(path)
		char_info = extract_character_info(data)
		campaign_id = compute_campaign_id(char_info)

		results[name] = {
			'character_info': char_info,
			'campaign_id': campaign_id
		}

		# Don't print Cyrillic to console (encoding issues on Windows)
		print(f"  Character data extracted")
		print(f"  Campaign ID: {campaign_id}")

	# Validation
	print("\n" + "=" * 80)
	print("VALIDATION")
	print("=" * 80)

	c1s1_id = results['C1S1']['campaign_id']
	c1s2_id = results['C1S2']['campaign_id']
	c2s1_id = results['C2S1']['campaign_id']
	c2s2_id = results['C2S2']['campaign_id']

	print(f"\n  Campaign 1 Save 1 ID: {c1s1_id}")
	print(f"  Campaign 1 Save 2 ID: {c1s2_id}")
	print(f"  Campaign 2 Save 1 ID: {c2s1_id}")
	print(f"  Campaign 2 Save 2 ID: {c2s2_id}")

	c1_match = (c1s1_id == c1s2_id)
	c2_match = (c2s1_id == c2s2_id)
	campaigns_differ = (c1s1_id != c2s1_id)

	print(f"\n  [OK] Campaign 1 saves have same ID: {c1_match}")
	print(f"  [OK] Campaign 2 saves have same ID: {c2_match}")
	print(f"  [OK] Campaigns have different IDs: {campaigns_differ}")

	if c1_match and c2_match and campaigns_differ:
		print("\n" + "=" * 80)
		print("*** SUCCESS! COMPOSITE CAMPAIGN ID WORKS! ***")
		print("=" * 80)
		print(f"\n  Campaign 1 ID: {c1s1_id}")
		print(f"  Campaign 2 ID: {c2s1_id}")
		print("\n  You can use this ID to match saves to campaigns!")

	# Save results
	output_file = Path('tmp/campaign_ids.json')
	output_file.parent.mkdir(exist_ok=True)

	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(results, f, ensure_ascii=False, indent=2)

	print(f"\n  Results saved to: {output_file}")


if __name__ == '__main__':
	main()
