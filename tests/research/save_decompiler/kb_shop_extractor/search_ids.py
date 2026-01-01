#!/usr/bin/env python3
"""
Search for shop and item IDs in decompressed save data
"""
import re


def search_patterns(file_path: str):
	"""Search for shop and item ID patterns"""
	with open(file_path, 'rb') as f:
		data = f.read()

	# Convert to string for searching (errors='ignore' to skip invalid bytes)
	text = data.decode('ascii', errors='ignore')

	print("=== Searching for ID Patterns ===\n")

	# Shop ID pattern: itext_m_*
	print("[1] Searching for shop IDs (itext_m_*)...")
	shop_pattern = r'itext_m_\w+'
	shop_matches = re.findall(shop_pattern, text)
	shop_unique = list(set(shop_matches))

	print(f"    Found {len(shop_matches)} total matches")
	print(f"    Found {len(shop_unique)} unique shop IDs")
	if shop_unique:
		print(f"    Examples:")
		for shop_id in sorted(shop_unique)[:10]:
			print(f"      - {shop_id}")

	# Item ID pattern: itm_*
	print(f"\n[2] Searching for item IDs (itm_*)...")
	item_pattern = r'itm_\w+'
	item_matches = re.findall(item_pattern, text)
	item_unique = list(set(item_matches))

	print(f"    Found {len(item_matches)} total matches")
	print(f"    Found {len(item_unique)} unique item IDs")
	if item_unique:
		print(f"    Examples:")
		for item_id in sorted(item_unique)[:10]:
			print(f"      - {item_id}")

	# Search for specific shop IDs
	print(f"\n[3] Searching for specific shop IDs...")
	test_shops = ['itext_m_galenirimm_2207', 'itext_m_helvedia_96']
	for shop_id in test_shops:
		if shop_id in text:
			offset = text.find(shop_id)
			print(f"    [+] Found '{shop_id}' at offset {offset}")
			# Show context around the match
			show_context(data, offset, shop_id)
		else:
			print(f"    [-] Not found: '{shop_id}'")

	# Search for specific item IDs
	print(f"\n[4] Searching for specific item IDs...")
	test_items = ['itm_addon3_weapon_grandpa_sword', 'itm_addon2_gauntlet_avrelii_gauntlet']
	for item_id in test_items:
		if item_id in text:
			offset = text.find(item_id)
			print(f"    [+] Found '{item_id}' at offset {offset}")
		else:
			print(f"    [-] Not found: '{item_id}'")

	return shop_unique, item_unique


def show_context(data: bytes, offset: int, string: str):
	"""Show hex context around a found string"""
	# Calculate byte offset
	byte_offset = 0
	for i in range(offset):
		try:
			if chr(data[byte_offset]) == string[0]:
				# Check if this is the actual match
				test = data[byte_offset:byte_offset+len(string)].decode('ascii', errors='ignore')
				if test == string[:len(test)]:
					break
			byte_offset += 1
		except:
			byte_offset += 1

	# Show 64 bytes before and after
	start = max(0, byte_offset - 64)
	end = min(len(data), byte_offset + len(string) + 64)
	context = data[start:end]

	print(f"\n    Hex context (64 bytes before/after):")
	for i in range(0, len(context), 16):
		hex_part = ' '.join(f'{b:02x}' for b in context[i:i+16])
		ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context[i:i+16])
		addr = start + i
		marker = ">>>" if start + i <= byte_offset < start + i + 16 else "   "
		print(f"    {marker} {addr:08x}: {hex_part:48s} {ascii_part}")


if __name__ == '__main__':
	import os
	script_dir = os.path.dirname(os.path.abspath(__file__))
	decompressed_file = os.path.join(script_dir, 'tmp', 'decompressed.bin')

	shop_ids, item_ids = search_patterns(decompressed_file)

	# Save results
	with open(os.path.join(script_dir, 'tmp', 'found_shop_ids.txt'), 'w') as f:
		for shop_id in sorted(shop_ids):
			f.write(f"{shop_id}\n")

	with open(os.path.join(script_dir, 'tmp', 'found_item_ids.txt'), 'w') as f:
		for item_id in sorted(item_ids):
			f.write(f"{item_id}\n")

	print(f"\n[+] Saved shop IDs to: tmp/found_shop_ids.txt")
	print(f"[+] Saved item IDs to: tmp/found_item_ids.txt")
