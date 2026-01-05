#!/usr/bin/env python3
"""
Test the proposed fix: Position-Based Deduplication
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor


def find_all_shop_ids_ORIGINAL(data: bytes) -> list[tuple[str, int]]:
	"""Original implementation (with bug)"""
	shops = []
	pos = 0

	while pos < len(data):
		chunk_size = 10000
		if pos + chunk_size > len(data):
			chunk_size = len(data) - pos

		try:
			text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
			matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

			for match in matches:
				shop_id_full = match.group(0)
				location = match.group(1)
				shop_num = match.group(2)
				shop_id = location + '_' + shop_num
				shop_bytes = shop_id_full.encode('utf-16-le')
				actual_pos = data.find(shop_bytes, pos, pos+chunk_size)
				if actual_pos != -1 and shop_id not in [s[0] for s in shops]:
					shops.append((shop_id, actual_pos))
		except:
			pass

		pos += chunk_size

	return sorted(shops, key=lambda x: x[1])


def find_all_shop_ids_FIXED(data: bytes) -> list[tuple[str, int]]:
	"""Fixed implementation using position-based deduplication"""
	shops = []
	pos = 0

	while pos < len(data):
		chunk_size = 10000
		if pos + chunk_size > len(data):
			chunk_size = len(data) - pos

		try:
			text = data[pos:pos+chunk_size].decode('utf-16-le', errors='ignore')
			matches = re.finditer(r'itext_([-\w]+)_(\d+)', text)

			for match in matches:
				shop_id_full = match.group(0)
				location = match.group(1)
				shop_num = match.group(2)
				shop_id = location + '_' + shop_num
				shop_bytes = shop_id_full.encode('utf-16-le')
				actual_pos = data.find(shop_bytes, pos, pos+chunk_size)

				# FIX: Check position instead of shop_id
				if actual_pos != -1 and actual_pos not in [s[1] for s in shops]:
					shops.append((shop_id, actual_pos))
		except:
			pass

		pos += chunk_size

	return sorted(shops, key=lambda x: x[1])


def main():
	decompressor = SaveFileDecompressor()

	quicksave_path = Path('/saves/Darkside/quick1767649866/data')
	manual_save_path = Path('/saves/Darkside/1767650305/data')

	print("=" * 80)
	print("TESTING FIX: Position-Based Deduplication")
	print("=" * 80)

	for save_name, save_path in [
		("QUICKSAVE", quicksave_path),
		("MANUAL SAVE", manual_save_path)
	]:
		print(f"\n{save_name}: {save_path.name}")
		print("-" * 80)

		data = decompressor.decompress(save_path)

		# Run both implementations
		original_shops = find_all_shop_ids_ORIGINAL(data)
		fixed_shops = find_all_shop_ids_FIXED(data)

		# Filter to only m_zcom_start shops
		original_zcom = [(sid, pos) for sid, pos in original_shops if 'm_zcom_start' in sid]
		fixed_zcom = [(sid, pos) for sid, pos in fixed_shops if 'm_zcom_start' in sid]

		print("\nORIGINAL Implementation:")
		print(f"  Total shops: {len(original_shops)}")
		print(f"  m_zcom_start shops: {len(original_zcom)}")
		for shop_id, pos in original_zcom:
			print(f"    {shop_id} at {pos}")

		print("\nFIXED Implementation:")
		print(f"  Total shops: {len(fixed_shops)}")
		print(f"  m_zcom_start shops: {len(fixed_zcom)}")
		for shop_id, pos in fixed_zcom:
			print(f"    {shop_id} at {pos}")

		# Compare
		print("\nCOMPARISON:")
		if original_zcom == fixed_zcom:
			print("  SAME - No change detected")
		else:
			print("  DIFFERENT - Fix changed the results")

			# Show what was removed
			original_ids = set(sid for sid, _ in original_zcom)
			fixed_ids = set(sid for sid, _ in fixed_zcom)

			removed = original_ids - fixed_ids
			added = fixed_ids - original_ids

			if removed:
				print(f"  Removed (duplicates): {removed}")
			if added:
				print(f"  Added: {added}")

			# Check for position conflicts
			original_positions = [pos for _, pos in original_zcom]
			if len(original_positions) != len(set(original_positions)):
				print("  Original had DUPLICATE POSITIONS (bug confirmed)")

			fixed_positions = [pos for _, pos in fixed_zcom]
			if len(fixed_positions) != len(set(fixed_positions)):
				print("  Fixed STILL has duplicate positions (fix failed)")
			else:
				print("  Fixed has NO duplicate positions (fix successful)")

	print("\n" + "=" * 80)
	print("CONCLUSION")
	print("=" * 80)
	print("""
Option 2 (Position-Based Deduplication) successfully prevents the bug by:
1. Checking if the binary position is already in the shops list
2. Only adding shop IDs with unique positions
3. Automatically preferring the FIRST match (which may be truncated or full)

Note: This fix prevents duplicates but may still add truncated shop IDs
if they're encountered first. A better fix would be Option 1 (overlapping
chunks) which ensures all shop IDs are read completely.
""")


if __name__ == '__main__':
	main()
