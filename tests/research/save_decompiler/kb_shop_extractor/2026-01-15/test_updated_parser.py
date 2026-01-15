#!/usr/bin/env python3
"""Test updated ShopInventoryParser2 with actor extraction"""

import sys
from pathlib import Path

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParserV2
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

print('=' * 80)
print('TESTING UPDATED ShopInventoryParser2')
print('=' * 80)
print()

parser = ShopInventoryParserV2(decompressor=SaveFileDecompressor())
save_path = Path('/app/tests/game_files/saves/1768403991')

print(f'Parsing save file: {save_path}')
print()

result = parser.parse(save_path)

print(f'Total shops found: {len(result)}')
print()

# Find dragondor shops
print('DRAGONDOR SHOPS:')
print('-' * 80)
dragondor_shops = {k: v for k, v in result.items() if k.startswith('dragondor')}

for shop_id in sorted(dragondor_shops.keys()):
	shop_data = dragondor_shops[shop_id]

	units = shop_data['units']
	spells = shop_data['spells']

	print(f'\n{shop_id}:')

	if units:
		print(f'  Units: {len(units)} types')
		for unit in units[:3]:
			print(f'    - {unit["name"]} x{unit["quantity"]}')
		if len(units) > 3:
			print(f'    ... and {len(units) - 3} more')

	if spells:
		print(f'  Spells: {len(spells)} types')
		for spell in spells[:3]:
			print(f'    - {spell["name"]} x{spell["quantity"]}')
		if len(spells) > 3:
			print(f'    ... and {len(spells) - 3} more')

	if not units and not spells:
		print('  (empty inventory)')

print()
print('=' * 80)
print()

# Check if we found the specific bocman shop
print('CHECKING FOR BOCMAN SHOP:')
print('-' * 80)

bocman_shop = None
for shop_id, shop_data in result.items():
	for unit in shop_data['units']:
		if unit['name'] == 'bocman' and unit['quantity'] == 1460:
			bocman_shop = shop_id
			break
	if bocman_shop:
		break

if bocman_shop:
	print(f'✓ Found bocman x1460 shop: {bocman_shop}')

	if 'actor_807991996' in bocman_shop:
		print()
		print('★★★ SUCCESS! Shop correctly identified as actor_807991996!')
	else:
		print()
		print(f'⚠ Shop ID does not contain actor_807991996')
		print(f'  Shop ID: {bocman_shop}')

	print()
	print('Full inventory:')
	shop_data = result[bocman_shop]
	for unit in shop_data['units']:
		print(f'  - {unit["name"]} x{unit["quantity"]}')
else:
	print('✗ bocman x1460 shop not found!')

print()
print('=' * 80)
