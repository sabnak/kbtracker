"""
King's Bounty Campaign Identifier Tool

Extracts a composite campaign identifier from save files based on hero character names.
Since the game doesn't store an explicit campaign ID, we use the hero's first and second
names to create a unique identifier via MD5 hash.

Usage:
	from tools.kb_campaign_identifier import extract_campaign_id

	campaign_id = extract_campaign_id(Path('path/to/save/data'))
	print(f"Campaign ID: {campaign_id}")
"""
from pathlib import Path
import struct
import zlib
import hashlib


def decompress_save_file(save_path: Path) -> bytes:
	"""
	Decompress King's Bounty save data file.

	File format:
	- 4 bytes: Magic "slcb"
	- 4 bytes: Decompressed size (uint32 LE)
	- 4 bytes: Compressed size (uint32 LE)
	- N bytes: zlib compressed data

	:param save_path:
		Path to save data file
	:return:
		Decompressed binary data
	"""
	with open(save_path, 'rb') as f:
		data = f.read()

	# Verify magic header
	magic = data[0:4]
	if magic != b'slcb':
		raise ValueError(f"Invalid save file format. Expected 'slcb', got {magic}")

	# Extract sizes
	decompressed_size = struct.unpack('<I', data[4:8])[0]
	compressed_size = struct.unpack('<I', data[8:12])[0]

	# Decompress
	compressed_data = data[12:12 + compressed_size]
	decompressed_data = zlib.decompress(compressed_data)

	if len(decompressed_data) != decompressed_size:
		raise ValueError(
			f"Size mismatch after decompression. "
			f"Expected {decompressed_size}, got {len(decompressed_data)}"
		)

	return decompressed_data


def _extract_utf16_string_at(data: bytes, offset: int, max_length: int = 100) -> str:
	"""
	Extract UTF-16LE string starting at offset.

	:param data:
		Binary data to read from
	:param offset:
		Starting position
	:param max_length:
		Maximum characters to read
	:return:
		Decoded string or empty string if invalid
	"""
	string_bytes = bytearray()
	i = offset

	while i < min(offset + max_length * 2, len(data) - 1):
		b1 = data[i]
		b2 = data[i + 1]

		# Null terminator
		if b1 == 0 and b2 == 0:
			break

		# Valid UTF-16LE character (Cyrillic or Latin)
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


def extract_hero_names(data: bytes) -> tuple[str, str]:
	"""
	Extract hero first and second names from decompressed save data.

	Scans the first 100KB for UTF-16LE Cyrillic strings that represent character names.
	Filters out common game keywords and returns the first two unique candidate names.

	Note: The first name found is usually the pet name, which we skip.
	The second and third names are the hero's first and second names.

	:param data:
		Decompressed save file data
	:return:
		Tuple of (first_name, second_name)
	"""
	candidates = []
	search_limit = min(100000, len(data))

	# Keywords to filter out (not character names)
	excluded_keywords = {
		'crap', 'flags', 'clouds', 'hero', 'nickname',
		'arena', 'enemy', 'player', 'shop', 'item',
		'spell', 'unit', 'quest', 'map'
	}

	i = 0
	while i < search_limit - 4:
		byte1 = data[i]
		byte2 = data[i + 1]

		# Check for start of Cyrillic UTF-16LE string
		if byte2 == 0x04 and 0x10 <= byte1 <= 0x4F:
			string = _extract_utf16_string_at(data, i)

			# Filter candidate names
			if string and 4 <= len(string) <= 20:
				string_lower = string.lower()
				if not any(keyword in string_lower for keyword in excluded_keywords):
					if string not in candidates:
						candidates.append(string)

			i += len(string.encode('utf-16-le')) if string else 2
		else:
			i += 1

		# Stop once we have enough candidates
		if len(candidates) >= 3:
			break

	# Return hero names (skip pet name at index 0)
	first_name = candidates[1] if len(candidates) > 1 else ""
	second_name = candidates[2] if len(candidates) > 2 else ""

	return first_name, second_name


def compute_campaign_id(first_name: str, second_name: str) -> str:
	"""
	Compute campaign identifier from hero names.

	Creates MD5 hash of combined first and second names.

	:param first_name:
		Hero's first name
	:param second_name:
		Hero's second name
	:return:
		Campaign ID as hex string
	"""
	combined = f"{first_name}|{second_name}"
	return hashlib.md5(combined.encode('utf-8')).hexdigest()


def extract_campaign_id(save_data_path: Path) -> dict[str, str]:
	"""
	Extract campaign identifier from a save file.

	:param save_data_path:
		Path to save 'data' file
	:return:
		Dictionary with campaign_id, first_name, and second_name
	"""
	data = decompress_save_file(save_data_path)
	first_name, second_name = extract_hero_names(data)
	campaign_id = compute_campaign_id(first_name, second_name)

	return {
		'campaign_id': campaign_id,
		'first_name': first_name,
		'second_name': second_name,
		'full_name': f"{first_name} {second_name}".strip()
	}


def main():
	"""CLI interface for testing the tool."""
	import sys

	if len(sys.argv) < 2:
		print("Usage: python kb_campaign_identifier.py <path_to_save_data_file>")
		print("\nExample:")
		print("  python kb_campaign_identifier.py path/to/save/1707078232/data")
		sys.exit(1)

	save_path = Path(sys.argv[1])

	if not save_path.exists():
		print(f"Error: File not found: {save_path}")
		sys.exit(1)

	try:
		result = extract_campaign_id(save_path)

		print("=" * 60)
		print("CAMPAIGN IDENTIFIER EXTRACTION")
		print("=" * 60)
		print(f"\nSave file: {save_path}")
		print(f"\nHero name: {result['full_name']}")
		print(f"  First name:  {result['first_name']}")
		print(f"  Second name: {result['second_name']}")
		print(f"\nCampaign ID: {result['campaign_id']}")

	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)


if __name__ == '__main__':
	main()
