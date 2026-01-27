"""
Find actual hero inventory (not castle inventory)
"""
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def search_for_hero_markers(data: bytes) -> None:
	"""
	Search for hero-specific markers
	"""
	print("=== Searching for Hero-Related Markers ===\n")

	markers = [
		b'.hero',
		b'.ehero',
		b'.player',
		b'.inventory',
		b'.backpack',
		b'.char',
		b'.character',
		b'hero_',
	]

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
			print(f"{marker.decode('ascii', errors='ignore'):20s}: {len(positions):4d} occurrences")
			print(f"  First 5 positions: {positions[:5]}")


def dump_around_ehero_sections(data: bytes) -> None:
	"""
	Dump data around .ehero sections
	"""
	print("\n=== Analyzing .ehero Sections ===\n")

	pos = 0
	count = 0
	while pos < len(data) and count < 5:
		pos = data.find(b'.ehero', pos)
		if pos == -1:
			break

		print(f"\n{count+1}. .ehero at position {pos}")

		# Dump 500 bytes after .ehero
		start = pos
		end = min(len(data), pos + 500)
		chunk = data[start:end]

		print("  Hex/ASCII dump (500 bytes after .ehero):")
		for i in range(0, len(chunk), 32):
			line = chunk[i:i+32]
			hex_part = ' '.join(f'{b:02x}' for b in line)
			ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
			print(f"  {start+i:08x}  {hex_part:72s}  {ascii_part}")

		pos += 1
		count += 1


def check_items_near_ehero(data: bytes) -> None:
	"""
	Check for .items sections near .ehero
	"""
	print("\n=== Looking for .items Near .ehero ===\n")

	ehero_positions = []
	pos = 0
	while pos < len(data):
		pos = data.find(b'.ehero', pos)
		if pos == -1:
			break
		ehero_positions.append(pos)
		pos += 1

	for ehero_pos in ehero_positions[:5]:
		# Search forward 5000 bytes for .items
		search_end = min(len(data), ehero_pos + 5000)
		chunk = data[ehero_pos:search_end]

		items_pos = chunk.find(b'.items')
		if items_pos != -1:
			abs_items_pos = ehero_pos + items_pos
			print(f"  .ehero at {ehero_pos:8d} → .items at {abs_items_pos:8d} (distance: {items_pos:4d} bytes)")


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes\n")

	search_for_hero_markers(data)
	dump_around_ehero_sections(data)
	check_items_near_ehero(data)
