#!/usr/bin/env python3
"""
King's Bounty Shop Extractor CLI

CLI wrapper for ShopInventoryParser.
Extracts shop inventory data from King's Bounty save files and exports to JSON.

Author: Claude (Anthropic)
Date: December 31, 2025
Version: 2.0.0
"""
import sys
import json
from pathlib import Path

from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller
from src.utils.parsers.save_data.IShopInventoryParser import IShopInventoryParser


def print_statistics(shops: dict) -> None:
	"""
	Print extraction statistics

	:param shops:
		Dictionary of shop data
	"""
	total_garrison = sum(len(s['garrison']) for s in shops.values())
	total_items = sum(len(s['items']) for s in shops.values())
	total_units = sum(len(s['units']) for s in shops.values())
	total_spells = sum(len(s['spells']) for s in shops.values())
	total_products = total_garrison + total_items + total_units + total_spells

	shops_with_garrison = sum(1 for s in shops.values() if s['garrison'])
	shops_with_items = sum(1 for s in shops.values() if s['items'])
	shops_with_units = sum(1 for s in shops.values() if s['units'])
	shops_with_spells = sum(1 for s in shops.values() if s['spells'])
	shops_with_any = sum(1 for s in shops.values() if s['garrison'] or s['items'] or s['units'] or s['spells'])

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
	"""Main entry point"""
	if len(sys.argv) < 2:
		print("King's Bounty Shop Extractor v2.0.0")
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

	save_path = Path(sys.argv[1])
	output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('shops.json')

	if not save_path.exists():
		print(f"Error: Save file not found: {save_path}")
		sys.exit(1)

	try:
		container = Container()
		installer = DefaultInstaller(container)
		installer.install()
		container.wire(modules=[__name__])

		print("="*78)
		print("KING'S BOUNTY SHOP EXTRACTOR")
		print("="*78)
		print()
		print(f"Input:  {save_path}")
		print(f"Output: {output_path}")
		print()

		print("Extracting shop data...")
		parser: IShopInventoryParser = container.shop_inventory_parser()
		shops = parser.parse(save_path)

		print()
		print("Saving to JSON...")
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(shops, f, indent=2, ensure_ascii=False)

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
