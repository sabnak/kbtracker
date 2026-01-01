#!/usr/bin/env python3
"""
Example usage of King's Bounty Shop Extractor

This script demonstrates how to use the shop extractor programmatically.
"""
import json
from pathlib import Path
from kb_shop_extractor import (
	decompress_save_file,
	extract_shops,
	save_to_json,
	print_statistics
)


def example_extract_and_analyze():
	"""
	Example: Extract shops and perform basic analysis.
	"""
	# Path to your save file
	save_path = Path("../tmp/decompressed_new.bin")

	# For actual use, you would decompress first:
	# save_path = Path("path/to/saves/1767209722/data")
	# data = decompress_save_file(save_path)

	# For this example, we'll load pre-decompressed data
	with open(save_path, 'rb') as f:
		data = f.read()

	print("="*78)
	print("EXAMPLE: Extracting and Analyzing Shops")
	print("="*78)
	print()

	# Extract shops
	shops = extract_shops(data, verbose=True)

	# Save to JSON
	output_path = Path("example_output.json")
	save_to_json(shops, output_path)

	# Print statistics
	print_statistics(shops)

	print()
	print("="*78)
	print("EXAMPLE: Analyzing Specific Shops")
	print("="*78)
	print()

	# Find shops with most items
	shops_by_items = sorted(shops, key=lambda s: len(s['items']), reverse=True)
	print("Top 5 shops with most items:")
	for i, shop in enumerate(shops_by_items[:5], 1):
		print(f"  {i}. {shop['shop_id']:40s} - {len(shop['items'])} items")

	print()

	# Find shops with stackable items (qty > 1)
	print("Shops with stackable items:")
	for shop in shops:
		stackable = [(name, qty) for name, qty in shop['items'] if qty > 1]
		if stackable:
			print(f"  {shop['shop_id']}:")
			for name, qty in stackable:
				print(f"    - {name:30s} x{qty}")

	print()

	# Find largest unit quantities
	print("Largest unit quantities:")
	all_units = []
	for shop in shops:
		for name, qty in shop['units']:
			all_units.append((shop['shop_id'], name, qty))

	all_units.sort(key=lambda x: x[2], reverse=True)
	for shop_id, name, qty in all_units[:5]:
		print(f"  {shop_id:40s} - {name:20s} x{qty:,}")

	print()
	print(f"Results saved to: {output_path}")


def example_filter_by_item():
	"""
	Example: Find all shops selling a specific item.
	"""
	# Load extracted data
	with open("example_output.json", 'r', encoding='utf-8') as f:
		shops_data = json.load(f)

	print()
	print("="*78)
	print("EXAMPLE: Find Shops Selling Specific Item")
	print("="*78)
	print()

	# Search for shops selling crystals
	search_item = "addon4_3_crystal"
	print(f"Searching for shops selling: {search_item}")
	print()

	found_shops = []
	for shop_id, shop in shops_data.items():
		for item in shop['items']:
			if item['name'] == search_item:
				found_shops.append((shop_id, item['quantity']))

	if found_shops:
		print(f"Found in {len(found_shops)} shops:")
		for shop_id, qty in found_shops:
			print(f"  {shop_id:40s} - Quantity: {qty}")
	else:
		print(f"Item '{search_item}' not found in any shop")


def example_export_summary():
	"""
	Example: Create a summary report.
	"""
	# Load extracted data
	with open("example_output.json", 'r', encoding='utf-8') as f:
		shops_data = json.load(f)

	print()
	print("="*78)
	print("EXAMPLE: Generate Summary Report")
	print("="*78)
	print()

	summary = {
		'total_shops': len(shops_data),
		'unique_items': set(),
		'unique_units': set(),
		'unique_spells': set(),
		'shops_by_location': {}
	}

	for shop_id, shop in shops_data.items():
		# Extract location from shop_id (e.g., "itext_m_portland_6820" -> "portland")
		parts = shop_id.split('_')
		if len(parts) >= 3:
			location = parts[2]
			summary['shops_by_location'][location] = summary['shops_by_location'].get(location, 0) + 1

		# Collect unique items
		for item in shop['items']:
			summary['unique_items'].add(item['name'])
		for unit in shop['units']:
			summary['unique_units'].add(unit['name'])
		for spell in shop['spells']:
			summary['unique_spells'].add(spell['name'])

	print(f"Total shops: {summary['total_shops']}")
	print(f"Unique items: {len(summary['unique_items'])}")
	print(f"Unique units: {len(summary['unique_units'])}")
	print(f"Unique spells: {len(summary['unique_spells'])}")
	print()
	print("Shops by location:")
	for location, count in sorted(summary['shops_by_location'].items(), key=lambda x: x[1], reverse=True)[:10]:
		print(f"  {location:20s} - {count} shops")


if __name__ == '__main__':
	# Run examples
	example_extract_and_analyze()
	example_filter_by_item()
	example_export_summary()

	print()
	print("="*78)
	print("All examples completed successfully!")
	print("="*78)
