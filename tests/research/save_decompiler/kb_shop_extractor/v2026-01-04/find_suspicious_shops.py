"""Find suspicious shops for validation"""
from pathlib import Path
import sys

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

save_path = Path('/app/tests/game_files/saves/1707047253/data')
data = parser.parse(save_path)

print(f'Total shops parsed: {len(data)}\n')

# Find shops with short-named entities (test length fix)
print('=' * 70)
print('Shops with short-named entities (length < 5):')
print('=' * 70)
short_name_shops = []
for shop_id, shop_data in data.items():
	short_items = [item for item in shop_data['items'] if len(item['name']) < 5]
	short_units = [unit for unit in shop_data['units'] if len(unit['name']) < 5]
	short_spells = [spell for spell in shop_data['spells'] if len(spell['name']) < 5]

	if short_items or short_units or short_spells:
		short_name_shops.append(shop_id)
		print(f'\n{shop_id}:')
		if short_items:
			print(f'  Short items: {[i["name"] for i in short_items]}')
		if short_units:
			print(f'  Short units: {[u["name"] for u in short_units]}')
		if short_spells:
			print(f'  Short spells: {[s["name"] for s in short_spells]}')

print(f'\nTotal shops with short names: {len(short_name_shops)}')

# Find shops with many items/spells/units (good test cases)
print('\n' + '=' * 70)
print('Shops with lots of inventory (good for validation):')
print('=' * 70)
large_shops = []
for shop_id, shop_data in data.items():
	total = len(shop_data['items']) + len(shop_data['units']) + len(shop_data['spells'])
	if total > 20:
		large_shops.append((shop_id, total, shop_data))

large_shops.sort(key=lambda x: x[1], reverse=True)

for shop_id, total, shop_data in large_shops[:5]:
	print(f'\n{shop_id} (total: {total}):')
	print(f'  Items: {len(shop_data["items"])}')
	print(f'  Units: {len(shop_data["units"])}')
	print(f'  Spells: {len(shop_data["spells"])}')
	print(f'  Garrison: {len(shop_data["garrison"])}')

# Find shops with unusual patterns
print('\n' + '=' * 70)
print('Recommended shops for verification:')
print('=' * 70)

recommendations = []

# Shop with short names
if 'atrixus_late_708' in data:
	recommendations.append(('atrixus_late_708', 'Has short-named entities (trap, imp, imp2)'))

# Pick a few large shops
for shop_id, total, _ in large_shops[:3]:
	if shop_id not in [r[0] for r in recommendations]:
		recommendations.append((shop_id, f'Large inventory ({total} items)'))

# Shops with garrison
garrison_shops = [(shop_id, len(shop_data['garrison']))
				  for shop_id, shop_data in data.items()
				  if len(shop_data['garrison']) > 0]
garrison_shops.sort(key=lambda x: x[1], reverse=True)
if garrison_shops:
	shop_id, count = garrison_shops[0]
	if shop_id not in [r[0] for r in recommendations]:
		recommendations.append((shop_id, f'Has garrison ({count} units)'))

print('\nTop 5 shops to verify in-game:')
for i, (shop_id, reason) in enumerate(recommendations[:5], 1):
	print(f'\n{i}. {shop_id}')
	print(f'   Reason: {reason}')
	shop_data = data[shop_id]
	print(f'   Items: {len(shop_data["items"])}, Units: {len(shop_data["units"])}, Spells: {len(shop_data["spells"])}, Garrison: {len(shop_data["garrison"])}')

