"""
Investigate specific positions where hero items were found
"""
import struct
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def scan_backwards_for_section(data: bytes, pos: int, distance: int = 5000) -> None:
	"""
	Scan backwards from position to find section markers

	:param data:
		Decompressed save data
	:param pos:
		Starting position
	:param distance:
		Distance to scan backwards
	"""
	start = max(0, pos - distance)
	chunk = data[start:pos]

	section_markers = [
		b'.garrison',
		b'.items',
		b'.spells',
		b'.shopunits',
		b'.temp',
		b'.hero',
		b'.inventory',
		b'.equipment',
		b'.backpack',
		b'itext_',
		b'building_trader@',
	]

	print(f"\nScanning backwards from position {pos} (distance: {distance} bytes)")

	for marker in section_markers:
		positions = []
		search_pos = 0
		while search_pos < len(chunk):
			found = chunk.find(marker, search_pos)
			if found == -1:
				break
			positions.append(start + found)
			search_pos = found + 1

		if positions:
			print(f"  {marker.decode('ascii', errors='ignore'):20s}: {positions}")


def dump_hex_around(data: bytes, pos: int, before: int = 100, after: int = 100) -> None:
	"""
	Dump hex data around a position

	:param data:
		Decompressed save data
	:param pos:
		Center position
	:param before:
		Bytes before position
	:param after:
		Bytes after position
	"""
	start = max(0, pos - before)
	end = min(len(data), pos + after)
	chunk = data[start:end]

	print(f"\nHex dump around position {pos} (±{before}/{after} bytes):")
	for i in range(0, len(chunk), 32):
		line = chunk[i:i+32]
		hex_part = ' '.join(f'{b:02x}' for b in line)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
		abs_pos = start + i
		marker = " <-- TARGET" if start + i <= pos < start + i + 32 else ""
		print(f"{abs_pos:08x}  {hex_part:72s}  {ascii_part}{marker}")


def parse_slruck_metadata(data: bytes, item_pos: int, item_name: str) -> None:
	"""
	Parse slruck metadata after item name

	:param data:
		Decompressed save data
	:param item_pos:
		Position of item kb_id
	:param item_name:
		Item kb_id
	"""
	print(f"\nParsing metadata for '{item_name}' at position {item_pos}")

	# Skip to after item name
	start = item_pos + len(item_name)
	search_area = data[start:start + 500]

	# Find slruck
	slruck_pos = search_area.find(b'slruck')
	if slruck_pos == -1:
		print("  No slruck metadata found")
		return

	abs_slruck_pos = start + slruck_pos
	print(f"  Found slruck at offset +{slruck_pos} (absolute: {abs_slruck_pos})")

	# Parse slruck value
	try:
		value_start = slruck_pos + 6
		if value_start + 4 > len(search_area):
			return

		value_length = struct.unpack('<I', search_area[value_start:value_start+4])[0]
		value_data_start = value_start + 4

		if value_data_start + value_length > len(search_area):
			return

		value = search_area[value_data_start:value_data_start+value_length].decode('ascii', errors='ignore')
		print(f"  slruck value: '{value}' (length: {value_length})")

		if ',' in value:
			parts = value.split(',')
			if len(parts) == 2:
				print(f"  Parsed: slot={parts[0]}, quantity={parts[1]}")

	except Exception as e:
		print(f"  Error parsing slruck: {e}")


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes")

	# Investigate positions where hero items were found
	hero_items = [
		(120973, "knight_shield"),
		(140242, "knight_sword"),
		(569441, "tournament_helm"),
		(622194, "vampire_ring"),
		(547344, "ogr_belt"),
		(549163, "addon4_3_crystal"),
	]

	for pos, name in hero_items:
		print("\n" + "=" * 80)
		print(f"Investigating: {name} at position {pos}")
		print("=" * 80)

		scan_backwards_for_section(data, pos, distance=10000)
		parse_slruck_metadata(data, pos, name)
		dump_hex_around(data, pos, before=50, after=100)
