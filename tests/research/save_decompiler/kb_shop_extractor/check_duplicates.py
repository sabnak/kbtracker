"""
Check for duplicate shop IDs at different positions
to diagnose the empty inventory issue
"""
from pathlib import Path
from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParser
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from collections import defaultdict


def check_duplicate_shop_ids():
	"""
	Check if same shop_id appears at multiple positions

	This would explain why shops have empty inventories - later
	occurrences might overwrite earlier ones in the result dict.
	"""
	decompressor = SaveFileDecompressor()
	parser = ShopInventoryParser(decompressor)

	data = decompressor.decompress(Path("/saves/Darkside/1767650305/data"))
	shops = parser._find_all_shop_ids(data)

	by_id = defaultdict(list)
	for shop_id, pos in shops:
		by_id[shop_id].append(pos)

	duplicates = {sid: positions for sid, positions in by_id.items() if len(positions) > 1}

	print("=" * 80)
	print("DUPLICATE SHOP ID ANALYSIS")
	print("=" * 80)
	print(f"\nTotal shop entries found: {len(shops)}")
	print(f"Unique shop IDs: {len(by_id)}")
	print(f"Shop IDs appearing multiple times: {len(duplicates)}")

	if duplicates:
		print(f"\n" + "-" * 80)
		print("DUPLICATE SHOP IDs (same ID at different positions):")
		print("-" * 80)
		for i, (sid, positions) in enumerate(sorted(duplicates.items())[:10], 1):
			print(f"\n{i}. shop_id: '{sid}'")
			print(f"   Appears {len(positions)} times at positions:")
			for pos in positions[:5]:
				print(f"     - {pos}")
			if len(positions) > 5:
				print(f"     ... and {len(positions) - 5} more")

		print(f"\n" + "=" * 80)
		print("ROOT CAUSE IDENTIFIED:")
		print("=" * 80)
		print("The position-based deduplication allows the same shop_id to appear")
		print("multiple times (at different positions). When building the result dict,")
		print("later occurrences overwrite earlier ones, potentially with empty data.")
		print()
		print("SOLUTION:")
		print("Use BOTH deduplication strategies:")
		print("  1. seen_positions - prevents same position from being added twice")
		print("  2. seen_shop_ids  - prevents same shop_id from appearing multiple times")
	else:
		print(f"\n✓ No duplicate shop IDs found")
		print("The issue must be something else")


if __name__ == "__main__":
	check_duplicate_shop_ids()
