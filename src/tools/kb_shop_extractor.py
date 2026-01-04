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
import argparse
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
	parser = argparse.ArgumentParser(description='King\'s Bounty Shop Extractor')
	parser.add_argument('save_directory', type=Path, help='Path to King\'s Bounty save directory')
	args = parser.parse_args()

	save_dir = args.save_directory

	if not save_dir.exists():
		print(f"Error: Save directory not found: {save_dir}")
		sys.exit(1)

	if not save_dir.is_dir():
		print(f"Error: Path is not a directory: {save_dir}")
		sys.exit(1)

	save_data_path = save_dir / 'data'
	if not save_data_path.exists():
		print(f"Error: Save 'data' file not found in: {save_dir}")
		sys.exit(1)

	save_name = save_dir.name
	output_dir = Path('/tmp/save_export')
	output_dir.mkdir(parents=True, exist_ok=True)
	output_path = output_dir / f'{save_name}.json'

	try:
		container = Container()
		installer = DefaultInstaller(container)
		installer.install()
		container.wire(modules=[__name__])

		print("="*78)
		print("KING'S BOUNTY SHOP EXTRACTOR")
		print("="*78)
		print()
		print(f"Input:  {save_dir}")
		print(f"Output: {output_path}")
		print()

		print("Extracting shop data...")
		parser: IShopInventoryParser = container.shop_inventory_parser()
		shops = parser.parse(save_data_path)

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
