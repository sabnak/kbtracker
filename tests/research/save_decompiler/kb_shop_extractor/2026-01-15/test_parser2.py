#!/usr/bin/env python3
"""Test script comparing ShopInventoryParser and ShopInventoryParser2"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / '../../../../../'))

from src.utils.parsers.save_data.ShopInventoryParserOld import ShopInventoryParserOld
from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParserV2
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

def main():
	save_path = Path('/app/tests/game_files/saves/1768403991')

	decompressor = SaveFileDecompressor()

	parser1 = ShopInventoryParserOld(decompressor)
	parser2 = ShopInventoryParserV2(decompressor)

	print('Parsing with ShopInventoryParser (original)...')
	result1 = parser1.parse(save_path)
	print(f'Found {len(result1)} shops\n')

	print('Parsing with ShopInventoryParser2 (enhanced)...')
	result2 = parser2.parse(save_path)
	print(f'Found {len(result2)} shops\n')

	print('=' * 80)
	print('COMPARISON RESULTS')
	print('=' * 80)
	print()

	# Find new shops
	new_shops = set(result2.keys()) - set(result1.keys())
	print(f'New shops found by Parser2: {len(new_shops)}')
	print()

	# Group by location
	from collections import defaultdict
	by_location = defaultdict(list)

	for shop_id in new_shops:
		# Extract location (everything before _building_trader_ or last _)
		if '_building_trader_' in shop_id:
			location = shop_id.split('_building_trader_')[0]
		else:
			location = shop_id.rsplit('_', 1)[0]
		by_location[location].append(shop_id)

	# Display grouped by location
	for location in sorted(by_location.keys()):
		shops = by_location[location]
		print(f'{location}: ({len(shops)} new shops)')
		print('-' * 80)

		# Sort by the numeric ID at the end
		def get_shop_num(shop_id):
			try:
				return int(shop_id.split('_')[-1])
			except:
				return 0

		for shop_id in sorted(shops, key=get_shop_num)[:5]:
			shop_data = result2[shop_id]
			units = shop_data['units']

			print(f'  {shop_id}:')

			if units:
				unit_list = [f"{u['name']} x{u['quantity']}" for u in units[:4]]
				print(f'    Units: {", ".join(unit_list)}')
			else:
				print(f'    Units: (none)')

			spells = shop_data['spells']
			if spells:
				spell_list = [f"{s['name']} x{s['quantity']}" for s in spells[:4]]
				print(f'    Spells: {", ".join(spell_list)}')

			print()

		if len(shops) > 5:
			print(f'  ... and {len(shops) - 5} more\n')

	print('=' * 80)
	print()

	# Check for the specific bocman shop in dragondor
	print('Checking for the missing bocman/monstera shop (dragondor_building_trader_31):')
	print('-' * 80)

	bocman_shops_dragondor = [
		shop_id for shop_id in result2.keys()
		if 'dragondor' in shop_id
		and any(u['name'] == 'bocman' and u['quantity'] > 1000 for u in result2[shop_id]['units'])
	]

	if bocman_shops_dragondor:
		for shop_id in bocman_shops_dragondor:
			shop_data = result2[shop_id]
			print(f'\nFOUND: {shop_id}')
			print(f'  Units:')
			for unit in shop_data['units']:
				print(f'    - {unit["name"]} x{unit["quantity"]}')
			print(f'  Spells:')
			for spell in shop_data['spells']:
				print(f'    - {spell["name"]} x{spell["quantity"]}')
	else:
		print('  NOT FOUND (unexpected!)')

	print()
	print('=' * 80)


if __name__ == '__main__':
	main()
