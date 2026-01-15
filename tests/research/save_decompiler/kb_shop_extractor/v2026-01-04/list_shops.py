"""List all shops found by current parser"""
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

print(f'Total shops found: {len(data)}')
print('\nShops containing "atrixus":')
for shop_id in sorted(data.keys()):
	if 'atrixus' in shop_id:
		shop_data = data[shop_id]
		print(f'  {shop_id}:')
		print(f'    Items: {len(shop_data["items"])}')
		print(f'    Units: {len(shop_data["units"])}')
		print(f'    Spells: {len(shop_data["spells"])}')
		print(f'    Garrison: {len(shop_data["garrison"])}')

