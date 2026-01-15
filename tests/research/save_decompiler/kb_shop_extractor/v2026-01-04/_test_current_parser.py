"""Test current parser output"""
from pathlib import Path
import sys
import json

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.ShopInventoryParserOld import ShopInventoryParserOld

# Manual instantiation without DI
decompressor = SaveFileDecompressor()
parser = ShopInventoryParserOld(
	decompressor=decompressor,
	item_repository=None,  # We don't need repos for parsing
	spell_repository=None,
	unit_repository=None,
	shop_repository=None,
	shop_inventory_repository=None
)

save_path = Path('/app/tests/game_files/saves/1707047253/data')
data = parser.parse(save_path)

# Test specific shop
test_shops = ['zcom_519']

for shop_id in test_shops:
	print(f'\n{"=" * 70}')
	print(f'Testing Shop: {shop_id}')
	print(f'{"=" * 70}\n')
	if shop_id in data:
		shop_data = data[shop_id]

		print(f'Items ({len(shop_data["items"])}):')
		for item in shop_data['items']:
			print(f'  - {item["name"]} x{item["quantity"]}')

		print(f'\nUnits ({len(shop_data["units"])}):')
		for unit in shop_data['units']:
			print(f'  - {unit["name"]} x{unit["quantity"]}')

		print(f'\nSpells ({len(shop_data["spells"])}):')
		for spell in shop_data['spells']:
			print(f'  - {spell["name"]} x{spell["quantity"]}')

		print(f'\nGarrison ({len(shop_data["garrison"])}):')
		for g in shop_data['garrison']:
			print(f'  - {g["name"]} x{g["quantity"]}')
	else:
		print(f'Shop {shop_id} not found')

