"""
Find the correct .items section for hero inventory (not achievements)
"""
import struct
import re
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def dump_hex(data: bytes, start: int, size: int) -> None:
	"""Dump hex data"""
	end = min(len(data), start + size)
	chunk = data[start:end]

	for i in range(0, len(chunk), 32):
		line = chunk[i:i+32]
		hex_part = ' '.join(f'{b:02x}' for b in line)
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
		print(f"{start+i:08x}  {hex_part:72s}  {ascii_part}")


def find_section_markers_before(data: bytes, pos: int, distance: int) -> dict:
	"""Find all section markers before position"""
	start = max(0, pos - distance)
	chunk = data[start:pos]

	markers = {}
	for marker_bytes in [b'.items', b'.ehero', b'.army', b'.hero', b'.inventory', b'.actors']:
		positions = []
		search_pos = 0
		while True:
			found = chunk.find(marker_bytes, search_pos)
			if found == -1:
				break
			positions.append(start + found)
			search_pos = found + 1
		if positions:
			markers[marker_bytes.decode('ascii')] = positions

	return markers


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	# First hero item from cluster 15
	first_hero_item = "addon3_magic_ingridients"
	first_pos = 917274

	print(f"First hero item: {first_hero_item} at position {first_pos}")
	print("=" * 80)

	# Find section markers before it
	markers = find_section_markers_before(data, first_pos, distance=20000)

	print("\nSection markers within 20000 bytes before:")
	for marker_name, positions in markers.items():
		print(f"\n  {marker_name}:")
		for pos in positions[-5:]:  # Show last 5
			distance = first_pos - pos
			print(f"    {pos:8d} (distance: {distance:6d} bytes)")

	# Find the nearest .items before the hero item
	if '.items' in markers:
		nearest_items = markers['.items'][-1]
		print(f"\n{'='*80}")
		print(f"Nearest .items section: {nearest_items}")
		print(f"Distance to first hero item: {first_pos - nearest_items} bytes")
		print(f"{'='*80}")

		# Dump 500 bytes before and 2000 bytes after this .items
		print("\nHex dump around this .items section:")
		dump_hex(data, nearest_items - 500, 2500)
