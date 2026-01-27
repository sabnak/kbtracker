"""
Compare what appears before hero .items sections vs shop .items sections
"""
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def scan_before_items_section(data: bytes, items_pos: int, distance: int = 2000) -> dict:
	"""
	Scan area before .items section

	:param data:
		Decompressed save data
	:param items_pos:
		Position of .items section
	:param distance:
		Distance to scan backwards
	:return:
		Dict with markers found
	"""
	start = max(0, items_pos - distance)
	chunk = data[start:items_pos]

	markers = {
		b'.garrison': [],
		b'.hero': [],
		b'.inventory': [],
		b'.char': [],
		b'.player': [],
		b'.actors': [],
	}

	for marker, positions in markers.items():
		pos = 0
		while pos < len(chunk):
			found = chunk.find(marker, pos)
			if found == -1:
				break
			positions.append(start + found)
			pos = found + 1

	return markers


def dump_before_section(data: bytes, items_pos: int, size: int = 200) -> str:
	"""
	Dump hex/ASCII before .items section

	:param data:
		Decompressed save data
	:param items_pos:
		Position of .items section
	:param size:
		Bytes to dump
	:return:
		Formatted dump string
	"""
	start = max(0, items_pos - size)
	chunk = data[start:items_pos]

	lines = []
	for i in range(0, len(chunk), 32):
		line = chunk[i:i+32]
		hex_part = ' '.join(f'{b:02x}' for b in line)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
		lines.append(f"{start+i:08x}  {hex_part:72s}  {ascii_part}")

	return '\n'.join(lines)


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	# Hero .items sections
	hero_sections = [119932, 139551, 546889, 548957, 569249, 621517]

	# Regular shop .items sections
	shop_sections = [66449, 70965, 72793, 83586]

	print("=" * 100)
	print("HERO .items SECTIONS")
	print("=" * 100)

	for i, pos in enumerate(hero_sections, 1):
		print(f"\n{i}. Hero .items at {pos}")
		markers = scan_before_items_section(data, pos, distance=3000)

		print("\n  Markers found (within 3000 bytes before):")
		for marker, positions in markers.items():
			if positions:
				marker_str = marker.decode('ascii', errors='ignore')
				print(f"    {marker_str:15s}: {positions}")

		print(f"\n  Hex/ASCII dump (200 bytes before .items):")
		dump = dump_before_section(data, pos, size=200)
		print("  " + dump.replace('\n', '\n  '))
		print()

	print("\n" + "=" * 100)
	print("REGULAR SHOP .items SECTIONS")
	print("=" * 100)

	for i, pos in enumerate(shop_sections, 1):
		print(f"\n{i}. Shop .items at {pos}")
		markers = scan_before_items_section(data, pos, distance=3000)

		print("\n  Markers found (within 3000 bytes before):")
		for marker, positions in markers.items():
			if positions:
				marker_str = marker.decode('ascii', errors='ignore')
				print(f"    {marker_str:15s}: {positions}")

		print(f"\n  Hex/ASCII dump (200 bytes before .items):")
		dump = dump_before_section(data, pos, size=200)
		print("  " + dump.replace('\n', '\n  '))
		print()
