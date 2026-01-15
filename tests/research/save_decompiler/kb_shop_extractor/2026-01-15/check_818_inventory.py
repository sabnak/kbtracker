#!/usr/bin/env python3
"""Check inventory of building_trader@818"""

from pathlib import Path
import sys

sys.path.insert(0, '/app')

from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParserV2
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor

def main():
	save_path = Path('/app/tests/game_files/saves/1768403991')

	decompressor = SaveFileDecompressor()
	parser = ShopInventoryParserV2(decompressor)

	result = parser.parse(save_path)

	print('=' * 80)
	print('CHECKING building_trader@818 INVENTORY')
	print('=' * 80)
	print()

	# Find shop with actor_807991996 or building_trader_818
	shops_with_818 = [
		shop_id for shop_id in result.keys()
		if 'actor_807991996' in shop_id or 'building_trader_818' in shop_id
	]

	if shops_with_818:
		for shop_id in shops_with_818:
			shop_data = result[shop_id]
			print(f'Shop ID: {shop_id}')
			print('-' * 80)
			print()

			print('Units:')
			if shop_data['units']:
				for unit in shop_data['units']:
					print(f'  - {unit["name"]} x{unit["quantity"]}')
			else:
				print('  (none)')

			print()
			print('Spells:')
			if shop_data['spells']:
				for spell in shop_data['spells']:
					print(f'  - {spell["name"]} x{spell["quantity"]}')
			else:
				print('  (none)')

			print()
			print('Items:')
			if shop_data['items']:
				for item in shop_data['items']:
					print(f'  - {item["name"]} x{item["quantity"]}')
			else:
				print('  (none)')

			print()
	else:
		print('No shop found with building_trader_818 or actor_807991996')
		print()
		print('Let me search for shops in m_inselburg:')
		m_inselburg_shops = [
			shop_id for shop_id in result.keys()
			if 'm_inselburg' in shop_id
		]

		if m_inselburg_shops:
			print(f'Found {len(m_inselburg_shops)} shops in m_inselburg:')
			for shop_id in sorted(m_inselburg_shops):
				print(f'  - {shop_id}')
		else:
			print('  No shops found in m_inselburg either!')

	print()
	print('=' * 80)
	print()

	# Also show dragondor_building_trader_31
	print('For comparison, dragondor_building_trader_31:')
	print('-' * 80)

	dragondor_31 = [
		shop_id for shop_id in result.keys()
		if 'dragondor' in shop_id and ('31' in shop_id or 'building_trader_31' in shop_id)
	]

	if dragondor_31:
		for shop_id in dragondor_31:
			shop_data = result[shop_id]
			print(f'Shop ID: {shop_id}')
			print()

			print('Units:')
			for unit in shop_data['units'][:5]:
				print(f'  - {unit["name"]} x{unit["quantity"]}')

			print()
			print('Spells:')
			for spell in shop_data['spells'][:5]:
				print(f'  - {spell["name"]} x{spell["quantity"]}')

	print()
	print('=' * 80)


if __name__ == '__main__':
	main()
