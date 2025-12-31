#!/usr/bin/env python3
"""
King's Bounty Shop Extractor
=============================

Extracts shop inventory data from King's Bounty save files.

Author: Claude (Anthropic)
Date: December 31, 2025
Version: 1.0.0
"""
import struct
import re
import json
import zlib
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Metadata keywords to filter out (not actual items)
METADATA_KEYWORDS = {
	'count', 'flags', 'lvars', 'slruck', 'id', 'strg', 'bmd', 'ugid',
	'temp', 'hint', 'label', 'name', 'image', 'text', 's', 'h'
}


def is_valid_id(item_id: str) -> bool:
	"""
	Validate item/spell/unit ID.

	:param item_id:
		ID string to validate
	:return:
		True if valid, False otherwise
	"""
	if not item_id or item_id in METADATA_KEYWORDS or len(item_id) < 5:
		return False
	return bool(re.match(r'^[a-z][a-z0-9_]*$', item_id))


def decompress_save_file(save_path: Path) -> bytes:
	"""
	Decompress King's Bounty save file.

	Save file format:
	- 4 bytes: magic "slcb"
	- 4 bytes: decompressed size (uint32 LE)
	- 4 bytes: compressed size (uint32 LE)
	- N bytes: zlib compressed data

	:param save_path:
		Path to save file 'data' file
	:return:
		Decompressed binary data
	"""
	with open(save_path, 'rb') as f:
		# Read header
		magic = f.read(4)
		if magic != b'slcb':
			raise ValueError(f"Invalid save file magic: {magic}")

		decompressed_size = struct.unpack('<I', f.read(4))[0]
		compressed_size = struct.unpack('<I', f.read(4))[0]

		# Read and decompress
		compressed_data = f.read()

		decompressed = zlib.decompress(compressed_data)
		if len(decompressed) != decompressed_size:
			raise ValueError(f"Decompressed size mismatch: expected {decompressed_size}, got {len(decompressed)}")

		return decompressed


def find_all_shop_ids(data: bytes) -> List[Tuple[str, int]]:
	"""
	Find all shop IDs in save file.

	Shop IDs are UTF-16 LE encoded strings matching pattern: itext_m_<location>_<number>

	:param data:
		Decompressed save file data
	:return:
		List of (shop_id, position) tuples sorted by position
	"""
	shops = []
	pos = 0

	while pos < len(data):
		chunk_size = 10000
		if pos + chunk_size > len(data):
			chunk_size = len(data) - pos

		try:
			text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
			matches = re.finditer(r'itext_m_\w+_\d+', text)

			for match in matches:
				shop_id = match.group(0)
				shop_bytes = shop_id.encode('utf-16-le')
				actual_pos = data.find(shop_bytes, pos, pos+chunk_size)
				if actual_pos != -1 and shop_id not in [s[0] for s in shops]:
					shops.append((shop_id, actual_pos))
		except:
			pass

		pos += chunk_size

	return sorted(shops, key=lambda x: x[1])


def find_preceding_section(data: bytes, marker: bytes, shop_pos: int, max_distance: int = 5000) -> Optional[int]:
	"""
	Find section marker immediately before shop ID.

	:param data:
		Save file data
	:param marker:
		Section marker (e.g., b'.items')
	:param shop_pos:
		Shop ID position
	:param max_distance:
		Maximum distance to search backwards
	:return:
		Section position or None if not found
	"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos
	return None


def parse_slash_separated(data: bytes, section_pos: int, next_pos: int) -> List[Tuple[str, int]]:
	"""
	Parse slash-separated format: name/qty/name/qty/...

	Used by: .garrison and .shopunits sections

	:param data:
		Save file data
	:param section_pos:
		Section start position
	:param next_pos:
		Next section/shop position
	:return:
		List of (name, quantity) tuples
	"""
	pos = section_pos

	# Find 'strg' marker
	strg_pos = data.find(b'strg', pos, next_pos)
	if strg_pos == -1:
		return []

	pos = strg_pos + 4

	# Read string length
	if pos + 4 > len(data):
		return []

	str_length = struct.unpack('<I', data[pos:pos+4])[0]
	pos += 4

	if str_length <= 0 or str_length > 5000:
		return []

	if pos + str_length > len(data):
		return []

	# Read and parse string
	try:
		content_str = data[pos:pos+str_length].decode('ascii')
		parts = content_str.split('/')

		items = []
		i = 0
		while i < len(parts) - 1:
			name = parts[i]
			try:
				quantity = int(parts[i + 1])
				if is_valid_id(name):
					items.append((name, quantity))
				i += 2
			except:
				i += 1

		return items

	except:
		return []


def parse_items_section(data: bytes, section_pos: int, next_pos: int) -> List[Tuple[str, int]]:
	"""
	Parse items section.

	Quantity is stored in 'slruck' metadata field as "slot,quantity" string.
	Format: [length][name][metadata...slruck[length]["slot,qty"]...]

	:param data:
		Save file data
	:param section_pos:
		Section start position
	:param next_pos:
		Next section/shop position
	:return:
		List of (name, quantity) tuples
	"""
	items = []
	pos = section_pos + len(b'.items')
	search_end = next_pos

	while pos < search_end - 20:
		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 5 <= name_length <= 100:
				if pos + 4 + name_length > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					if is_valid_id(name):
						# Scan forward for slruck field
						scan_pos = pos + 4 + name_length
						quantity = 1  # Default

						for _ in range(125):  # Search next 500 bytes
							if scan_pos + 10 > search_end:
								break

							# Look for "slruck" string
							if data[scan_pos:scan_pos+6] == b'slruck':
								try:
									val_len = struct.unpack('<I', data[scan_pos+6:scan_pos+10])[0]
									if 1 <= val_len <= 20:
										val_str = data[scan_pos+10:scan_pos+10+val_len].decode('ascii', errors='strict')
										# Parse "slot,qty" format
										if ',' in val_str:
											parts = val_str.split(',')
											if len(parts) == 2:
												quantity = int(parts[1])
												break
								except:
									pass

							scan_pos += 1

						items.append((name, quantity))
						pos += 4 + name_length
						continue

				except:
					pass
		except:
			pass

		pos += 1

	return sorted(items)


def parse_spells_section(data: bytes, section_pos: int, next_pos: int) -> List[Tuple[str, int]]:
	"""
	Parse spells section.

	Quantity is stored as first uint32 after name.
	Format: [length][name][quantity][next spell...]

	:param data:
		Save file data
	:param section_pos:
		Section start position
	:param next_pos:
		Next section/shop position
	:return:
		List of (name, quantity) tuples
	"""
	spells_dict = {}
	pos = section_pos + len(b'.spells')
	search_end = next_pos

	while pos < search_end - 20:
		if pos + 4 > len(data):
			break

		try:
			name_length = struct.unpack('<I', data[pos:pos+4])[0]

			if 5 <= name_length <= 100:
				if pos + 4 + name_length + 4 > len(data):
					pos += 1
					continue

				try:
					name = data[pos+4:pos+4+name_length].decode('ascii', errors='strict')

					if is_valid_id(name):
						quantity = struct.unpack('<I', data[pos+4+name_length:pos+4+name_length+4])[0]

						if 0 < quantity < 10000:
							if name not in spells_dict or spells_dict[name] < quantity:
								spells_dict[name] = quantity

							pos += 4 + name_length + 4
							continue

				except:
					pass
		except:
			pass

		pos += 1

	return sorted(spells_dict.items())


def parse_shop(data: bytes, shop_id: str, shop_pos: int) -> Dict:
	"""
	Parse complete shop with all 4 sections.

	Shop structure:
	  [.garrison section]  <- Player's stored army (optional)
	  [.items section]     <- Equipment for sale
	  [.shopunits section] <- Units for hire
	  [.spells section]    <- Spells for purchase
	  [Shop ID UTF-16 LE]  <- "itext_m_<location>_<number>"

	:param data:
		Save file data
	:param shop_id:
		Shop identifier
	:param shop_pos:
		Shop ID position
	:return:
		Dictionary with shop data
	"""
	result = {
		'shop_id': shop_id,
		'garrison': [],
		'items': [],
		'units': [],
		'spells': []
	}

	# Find preceding sections (within 5KB before shop ID)
	garrison_pos = find_preceding_section(data, b'.garrison', shop_pos, 5000)
	items_pos = find_preceding_section(data, b'.items', shop_pos, 5000)
	units_pos = find_preceding_section(data, b'.shopunits', shop_pos, 5000)
	spells_pos = find_preceding_section(data, b'.spells', shop_pos, 5000)

	# Parse garrison (slash-separated format)
	if garrison_pos and items_pos:
		result['garrison'] = parse_slash_separated(data, garrison_pos, items_pos)

	# Parse items (slruck-based quantity)
	if items_pos:
		next_pos = units_pos if units_pos else (spells_pos if spells_pos else shop_pos)
		result['items'] = parse_items_section(data, items_pos, next_pos)

	# Parse units (slash-separated format)
	if units_pos:
		next_pos = spells_pos if spells_pos else shop_pos
		result['units'] = parse_slash_separated(data, units_pos, next_pos)

	# Parse spells (first uint32 after name)
	if spells_pos:
		result['spells'] = parse_spells_section(data, spells_pos, shop_pos)

	return result


def extract_shops(data: bytes, verbose: bool = True) -> List[Dict]:
	"""
	Extract all shops from decompressed save file.

	:param data:
		Decompressed save file data
	:param verbose:
		Print progress messages
	:return:
		List of shop dictionaries
	"""
	if verbose:
		print("Finding shop IDs...")

	shops = find_all_shop_ids(data)

	if verbose:
		print(f"Found {len(shops)} shops")
		print()

	all_shop_data = []

	for i, (shop_id, shop_pos) in enumerate(shops):
		if verbose and ((i + 1) % 50 == 0 or i == 0):
			print(f"  [{i+1}/{len(shops)}] Parsing shops...")

		shop_data = parse_shop(data, shop_id, shop_pos)
		all_shop_data.append(shop_data)

	return all_shop_data


def save_to_json(shops: List[Dict], output_path: Path) -> None:
	"""
	Save extracted shops to JSON file.

	:param shops:
		List of shop dictionaries
	:param output_path:
		Output JSON file path
	"""
	# Convert to JSON-friendly format
	json_data = {}
	for shop in shops:
		json_data[shop['shop_id']] = {
			'garrison': [{'name': n, 'quantity': q} for n, q in shop['garrison']],
			'items': [{'name': n, 'quantity': q} for n, q in shop['items']],
			'units': [{'name': n, 'quantity': q} for n, q in shop['units']],
			'spells': [{'name': n, 'quantity': q} for n, q in shop['spells']]
		}

	with open(output_path, 'w', encoding='utf-8') as f:
		json.dump(json_data, f, indent=2, ensure_ascii=False)


def print_statistics(shops: List[Dict]) -> None:
	"""
	Print extraction statistics.

	:param shops:
		List of shop dictionaries
	"""
	total_garrison = sum(len(s['garrison']) for s in shops)
	total_items = sum(len(s['items']) for s in shops)
	total_units = sum(len(s['units']) for s in shops)
	total_spells = sum(len(s['spells']) for s in shops)
	total_products = total_garrison + total_items + total_units + total_spells

	shops_with_garrison = sum(1 for s in shops if s['garrison'])
	shops_with_items = sum(1 for s in shops if s['items'])
	shops_with_units = sum(1 for s in shops if s['units'])
	shops_with_spells = sum(1 for s in shops if s['spells'])
	shops_with_any = sum(1 for s in shops if s['garrison'] or s['items'] or s['units'] or s['spells'])

	print()
	print("="*78)
	print("EXTRACTION STATISTICS")
	print("="*78)
	print()
	print(f"Total shops:           {len(shops)}")
	print(f"Shops with content:    {shops_with_any}")
	print(f"  - With garrison:     {shops_with_garrison}")
	print(f"  - With items:        {shops_with_items}")
	print(f"  - With units:        {shops_with_units}")
	print(f"  - With spells:       {shops_with_spells}")
	print()
	print(f"Total products:        {total_products}")
	print(f"  - Garrison units:    {total_garrison}")
	print(f"  - Items:             {total_items}")
	print(f"  - Units:             {total_units}")
	print(f"  - Spells:            {total_spells}")


def main():
	"""Main entry point."""
	if len(sys.argv) < 2:
		print("King's Bounty Shop Extractor v1.0.0")
		print()
		print("Usage:")
		print(f"  python {sys.argv[0]} <save_data_file> [output.json]")
		print()
		print("Arguments:")
		print("  save_data_file  Path to King's Bounty save 'data' file")
		print("  output.json     Output JSON file (default: shops.json)")
		print()
		print("Example:")
		print(f"  python {sys.argv[0]} saves/1234567890/data shops_output.json")
		sys.exit(1)

	# Parse arguments
	save_path = Path(sys.argv[1])
	output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('shops.json')

	# Validate input
	if not save_path.exists():
		print(f"Error: Save file not found: {save_path}")
		sys.exit(1)

	try:
		print("="*78)
		print("KING'S BOUNTY SHOP EXTRACTOR")
		print("="*78)
		print()
		print(f"Input:  {save_path}")
		print(f"Output: {output_path}")
		print()

		# Decompress save file
		print("Decompressing save file...")
		data = decompress_save_file(save_path)
		print(f"Decompressed size: {len(data):,} bytes")
		print()

		# Extract shops
		shops = extract_shops(data, verbose=True)

		# Save to JSON
		print()
		print("Saving to JSON...")
		save_to_json(shops, output_path)

		# Print statistics
		print_statistics(shops)

		print()
		print("="*78)
		print(f"SUCCESS: Extracted {len(shops)} shops to {output_path}")
		print("="*78)

	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)


if __name__ == '__main__':
	main()
