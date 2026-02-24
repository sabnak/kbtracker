"""
Analyze the .items section at 909699 (hero inventory)
"""
import struct
import re
from pathlib import Path

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def dump_hex_around(data: bytes, pos: int, before: int = 200, after: int = 500) -> None:
	"""Dump hex data around position"""
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


def scan_backwards_from_items(data: bytes, items_pos: int) -> None:
	"""Scan backwards from .items to find what precedes it"""
	start = max(0, items_pos - 5000)
	chunk = data[start:items_pos]

	print(f"\n=== Scanning 5000 bytes before .items at {items_pos} ===")

	markers = [
		b'.ehero',
		b'.hero',
		b'.actors',
		b'.castleruler1',
		b'.garrison',
		b'.face',
		b'.temp',
		b'itext_',
		b'building_trader@',
	]

	for marker in markers:
		marker_pos = chunk.rfind(marker)
		if marker_pos != -1:
			abs_pos = start + marker_pos
			print(f"  {marker.decode('ascii', errors='ignore'):20s} at {abs_pos:8d} (distance: {items_pos - abs_pos:5d} bytes)")


def count_items_in_section(data: bytes, items_pos: int, search_distance: int = 100000) -> int:
	"""
	Count how many valid item kb_ids are in the section

	:param data:
		Decompressed save data
	:param items_pos:
		Position of .items section
	:param search_distance:
		How far to search
	:return:
		Number of items found
	"""
	pos = items_pos + len(b'.items')
	search_end = min(len(data), items_pos + search_distance)

	count = 0
	found_items = []

	while pos < search_end and count < 300:  # Limit to first 300 items
		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 3 <= name_length <= 100:
				if pos + 4 + name_length > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					# Check if it looks like an item ID
					if re.match(r'^[a-z][a-z0-9_]*$', name):
						found_items.append(name)
						count += 1
						pos += 4 + name_length
						continue
				except:
					pass
		except:
			pass

		pos += 1

	return count, found_items


def check_if_shop(data: bytes, items_pos: int) -> tuple[bool, str]:
	"""Check if this .items belongs to a shop"""
	# Search forward 5000 bytes for shop identifiers
	search_end = min(len(data), items_pos + 5000)
	chunk = data[items_pos:search_end]

	# Check for itext_
	try:
		for offset in [0, 1]:
			text = chunk[offset:min(len(chunk), offset + 3000)].decode('utf-16-le', errors='ignore')
			match = re.search(r'itext_([-\w]+_\d+)', text)
			if match:
				return (True, f"itext: {match.group(1)}")
	except:
		pass

	# Check for building_trader@
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


if __name__ == "__main__":
	save_file = Path("/app/tests/game_files/saves/inventory1769382036")

	decompressor = SaveFileDecompressor()
	data = decompressor.decompress(save_file)

	# Hero inventory .items section
	hero_items_pos = 909699

	print(f"Analyzing .items section at position {hero_items_pos}")
	print("=" * 80)

	# Check if it's a shop
	is_shop, shop_info = check_if_shop(data, hero_items_pos)
	print(f"\nIs this a shop? {is_shop}")
	if is_shop:
		print(f"Shop info: {shop_info}")

	# Scan backwards
	scan_backwards_from_items(data, hero_items_pos)

	# Dump hex
	dump_hex_around(data, hero_items_pos, before=300, after=1000)

	# Count items
	print("\n" + "=" * 80)
	count, items = count_items_in_section(data, hero_items_pos, search_distance=200000)
	print(f"\nFound {count} items in this .items section")
	print(f"\nFirst 30 items:")
	for i, item in enumerate(items[:30], 1):
		print(f"  {i:3d}. {item}")
