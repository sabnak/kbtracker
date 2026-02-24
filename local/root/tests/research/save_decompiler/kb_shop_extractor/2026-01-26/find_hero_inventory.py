"""
Research script to find hero inventory patterns in save file
"""
import re
import struct
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def find_section_markers(data: bytes) -> None:
	"""
	Find all section markers in decompressed data
	"""
	markers = [
		b'.garrison',
		b'.items',
		b'.spells',
		b'.shopunits',
		b'.temp',
		b'.hero',
		b'.inventory',
		b'.equipment',
		b'.backpack',
		b'.armor',
		b'.weapon',
	]

	print("=== Section Markers Found ===")
	for marker in markers:
		positions = []
		pos = 0
		while pos < len(data):
			pos = data.find(marker, pos)
			if pos == -1:
				break
			positions.append(pos)
			pos += 1

		if positions:
			print(f"{marker.decode('ascii'):20s}: {len(positions):4d} occurrences at positions: {positions[:5]}...")


def search_for_item_kb_ids(data: bytes, known_items: list[str]) -> None:
	"""
	Search for known item kb_ids in the save file
	"""
	print("\n=== Searching for Known Item kb_ids ===")

	for item_id in known_items:
		# Search as UTF-16 LE
		item_bytes_utf16 = item_id.encode('utf-16-le')
		pos = data.find(item_bytes_utf16)

		if pos != -1:
			print(f"\nFound '{item_id}' (UTF-16 LE) at position {pos}")
			# Show context
			context_start = max(0, pos - 50)
			context_end = min(len(data), pos + len(item_bytes_utf16) + 50)
			context = data[context_start:context_end]
			print(f"Context (hex): {context.hex()}")

		# Search as ASCII
		item_bytes_ascii = item_id.encode('ascii')
		pos = data.find(item_bytes_ascii)

		if pos != -1:
			print(f"\nFound '{item_id}' (ASCII) at position {pos}")
			# Show context
			context_start = max(0, pos - 50)
			context_end = min(len(data), pos + len(item_bytes_ascii) + 50)
			context = data[context_start:context_end]
			print(f"Context (hex): {context.hex()}")


def find_length_prefixed_strings(data: bytes, min_length: int = 3, max_length: int = 100) -> None:
	"""
	Find length-prefixed ASCII strings (potential item kb_ids)
	"""
	print("\n=== Length-Prefixed ASCII Strings ===")

	pos = 0
	found_count = 0
	max_display = 50

	while pos < len(data) - 8 and found_count < max_display:
		if pos + 4 > len(data):
			break

		try:
			length = struct.unpack('<I', data[pos:pos+4])[0]

			if min_length <= length <= max_length:
				if pos + 4 + length > len(data):
					pos += 1
					continue

				try:
					string = data[pos+4:pos+4+length].decode('ascii', errors='strict')

					# Check if it looks like an item ID
					if re.match(r'^[a-z][a-z0-9_]*$', string):
						# Check what comes after
						next_bytes = data[pos+4+length:pos+4+length+8].hex() if pos+4+length+8 <= len(data) else "N/A"
						print(f"Pos {pos:8d}: [{length:3d}] '{string}' | Next 8 bytes: {next_bytes}")
						found_count += 1
				except:
					pass
		except:
			pass

		pos += 1


def scan_around_position(data: bytes, position: int, range_size: int = 500) -> None:
	"""
	Dump hex data around a specific position
	"""
	start = max(0, position - range_size)
	end = min(len(data), position + range_size)

	chunk = data[start:end]

	print(f"\n=== Hex dump around position {position} (±{range_size} bytes) ===")
	for i in range(0, len(chunk), 32):
		line = chunk[i:i+32]
		hex_part = ' '.join(f'{b:02x}' for b in line)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
		print(f"{start+i:08x}  {hex_part:72s}  {ascii_part}")


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")
	output_dir = Path("/app/tests/research/save_decompiler/kb_shop_extractor/2026-01-26/tmp")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes\n")

	# Save decompressed data
	with open(output_dir / "decompressed.bin", 'wb') as f:
		f.write(data)

	# Find section markers
	find_section_markers(data)

	# Search for actual equipment items from the database
	known_items = [
		"knight_shield",
		"knight_armor",
		"knight_sword",
		"tournament_helm",
		"knightly_boots",
		"vampire_ring",
		"mana_potion",
		"rage_potion",
		"addon4_3_crystal",
		"ogr_belt",
		"scaly_armor",
		"hunter_gloves",
	]

	search_for_item_kb_ids(data, known_items)

	# Find length-prefixed strings that could be item IDs
	find_length_prefixed_strings(data)
