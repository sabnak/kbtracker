"""Export all shop data to JSON and TXT formats"""
from pathlib import Path as FilePath
import sys
import json

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.ShopInventoryParserOld import ShopInventoryParserOld

# Manual instantiation
decompressor = SaveFileDecompressor()
parser = ShopInventoryParserOld(
	decompressor=decompressor,
	item_repository=None,
	spell_repository=None,
	unit_repository=None,
	shop_repository=None,
	shop_inventory_repository=None
)

save_path = FilePath('/app/tests/game_files/saves/1707047253/data')
data = parser.parse(save_path)

print(f'Total shops parsed: {len(data)}')

# Export to JSON
json_output = FilePath('/app/tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/all_shops_export.json')
with open(json_output, 'w', encoding='utf-8') as f:
	json.dump(data, f, indent=2, ensure_ascii=False)

print(f'JSON export complete: {json_output}')

# Export to readable TXT format
txt_output = FilePath('/app/tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/all_shops_export.txt')

with open(txt_output, 'w', encoding='utf-8') as f:
	f.write('=' * 80 + '\n')
	f.write('KING\'S BOUNTY - SHOP INVENTORY EXPORT\n')
	f.write('=' * 80 + '\n')
	f.write(f'Save file: 1707047253\n')
	f.write(f'Total shops: {len(data)}\n')
	f.write(f'Export date: 2026-01-04\n')
	f.write('=' * 80 + '\n\n')

	# Sort shops by ID for easier navigation
	sorted_shops = sorted(data.items(), key=lambda x: x[0])

	for shop_id, shop_data in sorted_shops:
		f.write('\n' + '=' * 80 + '\n')
		f.write(f'SHOP: {shop_id}\n')
		f.write('=' * 80 + '\n')

		# Summary
		total_items = len(shop_data['items'])
		total_units = len(shop_data['units'])
		total_spells = len(shop_data['spells'])
		total_garrison = len(shop_data['garrison'])
		f.write(f'Summary: {total_items} items, {total_units} units, {total_spells} spells, {total_garrison} garrison\n')
		f.write('\n')

		# Items
		if shop_data['items']:
			f.write(f'ITEMS ({total_items}):\n')
			for i, item in enumerate(shop_data['items'], 1):
				f.write(f'{i:3d}. {item["name"]} x{item["quantity"]}\n')
			f.write('\n')
		else:
			f.write('ITEMS: None\n\n')

		# Units
		if shop_data['units']:
			f.write(f'UNITS ({total_units}):\n')
			for i, unit in enumerate(shop_data['units'], 1):
				f.write(f'{i:3d}. {unit["name"]} x{unit["quantity"]}\n')
			f.write('\n')
		else:
			f.write('UNITS: None\n\n')

		# Spells
		if shop_data['spells']:
			f.write(f'SPELLS ({total_spells}):\n')
			for i, spell in enumerate(shop_data['spells'], 1):
				f.write(f'{i:3d}. {spell["name"]} x{spell["quantity"]}\n')
			f.write('\n')
		else:
			f.write('SPELLS: None\n\n')

		# Garrison
		if shop_data['garrison']:
			f.write(f'GARRISON ({total_garrison}):\n')
			for i, g in enumerate(shop_data['garrison'], 1):
				f.write(f'{i:3d}. {g["name"]} x{g["quantity"]}\n')
			f.write('\n')
		else:
			f.write('GARRISON: None\n\n')

print(f'TXT export complete: {txt_output}')

# Generate statistics
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

# Export statistics
stats_output = FilePath('/app/tests/research/save_decompiler/kb_shop_extractor/v2026-01-04/export_statistics.txt')
with open(stats_output, 'w', encoding='utf-8') as f:
	f.write('EXPORT STATISTICS\n')
	f.write('=' * 80 + '\n\n')
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

print(f'Statistics export complete: {stats_output}')

print('\n' + '=' * 80)
print('EXPORT SUMMARY')
print('=' * 80)
print(f'Total shops exported: {stats["total_shops"]}')
print(f'Total items: {stats["total_items"]}')
print(f'Total units: {stats["total_units"]}')
print(f'Total spells: {stats["total_spells"]}')
print(f'Total garrison: {stats["total_garrison"]}')
print('\nFiles created:')
print(f'  - all_shops_export.json (machine-readable)')
print(f'  - all_shops_export.txt (human-readable)')
print(f'  - export_statistics.txt (summary)')
