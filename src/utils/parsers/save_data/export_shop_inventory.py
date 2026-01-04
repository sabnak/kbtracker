#!/usr/bin/env python3
"""
Console tool for exporting shop inventory from King's Bounty save files

Usage:
    python export_shop_inventory.py /path/to/save/data
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParser


def export_shop_inventory(save_path: Path, output_dir: Path) -> None:
	"""
	Export shop inventory from save file to output directory

	:param save_path:
		Absolute path to save data file
	:param output_dir:
		Directory where to save export files
	"""
	if not save_path.exists():
		print(f'Error: Save file not found: {save_path}')
		sys.exit(1)

	if not save_path.is_file():
		print(f'Error: Path is not a file: {save_path}')
		sys.exit(1)

	output_dir.mkdir(parents=True, exist_ok=True)

	print(f'Parsing save file: {save_path}')

	decompressor = SaveFileDecompressor()
	parser = ShopInventoryParser(
		decompressor=decompressor,
		item_repository=None,
		spell_repository=None,
		unit_repository=None,
		shop_repository=None,
		shop_inventory_repository=None
	)

	data = parser.parse(save_path)

	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	save_name = save_path.parent.name

	json_file = output_dir / f'{save_name}_{timestamp}.json'
	txt_file = output_dir / f'{save_name}_{timestamp}.txt'
	stats_file = output_dir / f'{save_name}_{timestamp}_stats.txt'

	with open(json_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=2, ensure_ascii=False)

	with open(txt_file, 'w', encoding='utf-8') as f:
		_write_txt_export(f, data, save_name)

	with open(stats_file, 'w', encoding='utf-8') as f:
		_write_statistics(f, data, save_name)

	print(f'\nExport complete:')
	print(f'  JSON: {json_file}')
	print(f'  TXT:  {txt_file}')
	print(f'  Stats: {stats_file}')


def _write_txt_export(f, data: dict, save_name: str) -> None:
	"""Write human-readable text export"""
	f.write('=' * 80 + '\n')
	f.write('KING\'S BOUNTY - SHOP INVENTORY EXPORT\n')
	f.write('=' * 80 + '\n')
	f.write(f'Save: {save_name}\n')
	f.write(f'Total shops: {len(data)}\n')
	f.write(f'Export date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
	f.write('=' * 80 + '\n\n')

	sorted_shops = sorted(data.items(), key=lambda x: x[0])

	for shop_id, shop_data in sorted_shops:
		f.write('\n' + '=' * 80 + '\n')
		f.write(f'SHOP: {shop_id}\n')
		f.write('=' * 80 + '\n')

		total_items = len(shop_data['items'])
		total_units = len(shop_data['units'])
		total_spells = len(shop_data['spells'])
		total_garrison = len(shop_data['garrison'])
		f.write(f'Summary: {total_items} items, {total_units} units, {total_spells} spells, {total_garrison} garrison\n')
		f.write('\n')

		if shop_data['items']:
			f.write(f'ITEMS ({total_items}):\n')
			for i, item in enumerate(shop_data['items'], 1):
				f.write(f'{i:3d}. {item["name"]} x{item["quantity"]}\n')
			f.write('\n')
		else:
			f.write('ITEMS: None\n\n')

		if shop_data['units']:
			f.write(f'UNITS ({total_units}):\n')
			for i, unit in enumerate(shop_data['units'], 1):
				f.write(f'{i:3d}. {unit["name"]} x{unit["quantity"]}\n')
			f.write('\n')
		else:
			f.write('UNITS: None\n\n')

		if shop_data['spells']:
			f.write(f'SPELLS ({total_spells}):\n')
			for i, spell in enumerate(shop_data['spells'], 1):
				f.write(f'{i:3d}. {spell["name"]} x{spell["quantity"]}\n')
			f.write('\n')
		else:
			f.write('SPELLS: None\n\n')

		if shop_data['garrison']:
			f.write(f'GARRISON ({total_garrison}):\n')
			for i, g in enumerate(shop_data['garrison'], 1):
				f.write(f'{i:3d}. {g["name"]} x{g["quantity"]}\n')
			f.write('\n')
		else:
			f.write('GARRISON: None\n\n')


def _write_statistics(f, data: dict, save_name: str) -> None:
	"""Write export statistics"""
	stats = {
		'total_shops': len(data),
		'total_items': sum(len(shop['items']) for shop in data.values()),
		'total_units': sum(len(shop['units']) for shop in data.values()),
		'total_spells': sum(len(shop['spells']) for shop in data.values()),
		'total_garrison': sum(len(shop['garrison']) for shop in data.values()),
		'shops_with_items': sum(1 for shop in data.values() if len(shop['items']) > 0),
		'shops_with_units': sum(1 for shop in data.values() if len(shop['units']) > 0),
		'shops_with_spells': sum(1 for shop in data.values() if len(shop['spells']) > 0),
		'shops_with_garrison': sum(1 for shop in data.values() if len(shop['garrison']) > 0),
	}

	f.write('EXPORT STATISTICS\n')
	f.write('=' * 80 + '\n\n')
	f.write(f'Save: {save_name}\n')
	f.write(f'Export date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
	f.write(f'Total shops: {stats["total_shops"]}\n')
	f.write(f'Total items: {stats["total_items"]}\n')
	f.write(f'Total units: {stats["total_units"]}\n')
	f.write(f'Total spells: {stats["total_spells"]}\n')
	f.write(f'Total garrison: {stats["total_garrison"]}\n')
	f.write('\n')
	f.write(f'Shops with items: {stats["shops_with_items"]}\n')
	f.write(f'Shops with units: {stats["shops_with_units"]}\n')
	f.write(f'Shops with spells: {stats["shops_with_spells"]}\n')
	f.write(f'Shops with garrison: {stats["shops_with_garrison"]}\n')


def main():
	"""Main entry point"""
	if len(sys.argv) != 2:
		print('Usage: python export_shop_inventory.py <save_path>')
		print('Example: python export_shop_inventory.py /app/tests/game_files/saves/1707047253/data')
		sys.exit(1)

	save_path = Path(sys.argv[1])
	output_dir = Path('/tmp/save_export')

	try:
		export_shop_inventory(save_path, output_dir)
	except Exception as e:
		print(f'\nError: {type(e).__name__}: {e}')
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == '__main__':
	main()
