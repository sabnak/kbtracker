"""
Find the .items section that belongs to hero inventory
"""
import re
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def find_all_items_sections(data: bytes) -> list[int]:
	"""
	Find all .items section positions

	:param data:
		Decompressed save data
	:return:
		List of .items section positions
	"""
	positions = []
	pos = 0
	while pos < len(data):
		pos = data.find(b'.items', pos)
		if pos == -1:
			break
		positions.append(pos)
		pos += 1
	return positions


def check_if_shop_section(data: bytes, items_pos: int) -> tuple[bool, str]:
	"""
	Check if .items section belongs to a shop

	:param data:
		Decompressed save data
	:param items_pos:
		Position of .items section
	:return:
		Tuple of (is_shop, shop_identifier)
	"""
	# Search forward up to 5000 bytes for shop identifiers
	search_end = min(len(data), items_pos + 5000)
	chunk = data[items_pos:search_end]

	# Check for itext_ shop (UTF-16 LE)
	try:
		for offset in [0, 1]:
			if offset >= len(chunk):
				continue
			text = chunk[offset:min(len(chunk), offset + 3000)].decode('utf-16-le', errors='ignore')
			match = re.search(r'itext_([-\w]+_\d+)', text)
			if match:
				return (True, f"itext: {match.group(1)}")
	except:
		pass

	# Check for building_trader@ shop (ASCII)
	trader_pos = chunk.find(b'building_trader@')
	if trader_pos != -1 and trader_pos < 5000:
		try:
			segment = chunk[trader_pos:trader_pos+30]
			text = segment.decode('ascii', errors='ignore')
			match = re.match(r'building_trader@(\d+)', text)
			if match:
				return (True, f"building_trader: {match.group(1)}")
		except:
			pass

	return (False, "")


def analyze_items_in_section(data: bytes, items_pos: int, next_section_pos: int) -> dict:
	"""
	Analyze items in a .items section

	:param data:
		Decompressed save data
	:param items_pos:
		Position of .items section
	:param next_section_pos:
		Position of next section marker
	:return:
		Dict with analysis results
	"""
	items = []
	pos = items_pos + len(b'.items')
	search_end = min(next_section_pos, items_pos + 100000)  # Limit search

	count = 0
	while pos < search_end - 20 and count < 100:  # Limit to first 100 items
		if pos + 4 > len(data):
			break

		try:
			import struct
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 3 <= name_length <= 100:
				if pos + 4 + name_length > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					# Check if it looks like an item ID
					if re.match(r'^[a-z][a-z0-9_]*$', name):
						items.append(name)
						count += 1
						pos += 4 + name_length
						continue
				except:
					pass
		except:
			pass

		pos += 1

	return {
		'item_count': len(items),
		'sample_items': items[:10]
	}


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	print(f"Decompressed save file size: {len(data)} bytes\n")

	# Find all .items sections
	items_sections = find_all_items_sections(data)
	print(f"Found {len(items_sections)} .items sections\n")

	# Known hero item positions from previous investigation
	known_hero_positions = [120973, 140242, 569441, 622194, 547344, 549163]

	# Find which .items section each hero item belongs to
	print("Mapping hero items to .items sections:\n")
	hero_sections = set()

	for hero_pos in known_hero_positions:
		# Find nearest .items section before this position
		nearest = None
		for items_pos in items_sections:
			if items_pos < hero_pos:
				if nearest is None or items_pos > nearest:
					nearest = items_pos

		if nearest:
			hero_sections.add(nearest)
			distance = hero_pos - nearest
			print(f"  Hero item at {hero_pos:8d} → .items at {nearest:8d} (distance: {distance:5d} bytes)")

	print(f"\nUnique .items sections containing hero items: {len(hero_sections)}")
	print(f"Positions: {sorted(hero_sections)}\n")

	# Check first 20 .items sections
	print("=" * 100)
	print("Analyzing first 20 .items sections:")
	print("=" * 100)

	for i, items_pos in enumerate(items_sections[:20]):
		is_shop, shop_id = check_if_shop_section(data, items_pos)

		# Find next section
		next_pos = items_sections[i + 1] if i + 1 < len(items_sections) else len(data)

		# Analyze items
		analysis = analyze_items_in_section(data, items_pos, next_pos)

		is_hero = items_pos in hero_sections

		print(f"\n{i+1:3d}. Position: {items_pos:8d} {'[HERO]' if is_hero else ''}")
		print(f"     Shop: {str(is_shop):5s} {shop_id if is_shop else ''}")
		print(f"     Items: {analysis['item_count']} found")
		print(f"     Sample: {', '.join(analysis['sample_items'][:5])}")
