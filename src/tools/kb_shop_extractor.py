import argparse
import json
import sys
from pathlib import Path

import pydantic

from src.tools.CLITool import CLITool, T


class LaunchParams(pydantic.BaseModel):

	save_directory: Path


class KBShopSaveExtractorCLI(CLITool[LaunchParams]):

	_shops: dict
	_boundary = "=" * 78

	def _build_params(self) -> T:
		p = argparse.ArgumentParser(description='King\'s Bounty Shop Extractor')
		p.add_argument('save_directory', type=Path, help='Path to King\'s Bounty save directory')
		args = p.parse_args()
		return LaunchParams(save_directory=args.save_directory)

	def _run(self):
		self._shops = dict()
		parser = self._container.shop_inventory_parser()

		if not self._launch_params.save_directory.exists():
			print(f"Error: Save directory not found: {self._launch_params.save_directory}")
			sys.exit(1)

		if not self._launch_params.save_directory.is_dir():
			print(f"Error: Path is not a directory: {self._launch_params.save_directory}")
			sys.exit(1)

		save_data_path = self._launch_params.save_directory / 'data'
		if not save_data_path.exists():
			print(f"Error: Save 'data' file not found in: {self._launch_params.save_directory}")
			sys.exit(1)

		save_name = self._launch_params.save_directory.name
		output_dir = Path('/tmp/save_export')
		output_dir.mkdir(parents=True, exist_ok=True)
		output_path = output_dir / f'{save_name}.json'

		print(
			self._boundary,
			"KING'S BOUNTY SHOP EXTRACTOR",
			self._boundary,
			f"Input:  {self._launch_params.save_directory}",
			f"Output: {output_path}\n",
			"Extracting shop data...",
			sep="\n"
		)

		self._shops = parser.parse(save_data_path)

		print("\nSaving to JSON...")
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(self._shops, f, indent=2, ensure_ascii=False)

		self._print_statistics()

		print(
			"",
			self._boundary,
			f"SUCCESS: Extracted {len(self._shops)} shops to {output_path}",
			self._boundary,
			sep="\n"
		)

	def _print_statistics(self) -> None:
		total_garrison = sum(len(s['garrison']) for s in self._shops.values())
		total_items = sum(len(s['items']) for s in self._shops.values())
		total_units = sum(len(s['units']) for s in self._shops.values())
		total_spells = sum(len(s['spells']) for s in self._shops.values())
		total_products = total_garrison + total_items + total_units + total_spells

		shops_with_garrison = sum(1 for s in self._shops.values() if s['garrison'])
		shops_with_items = sum(1 for s in self._shops.values() if s['items'])
		shops_with_units = sum(1 for s in self._shops.values() if s['units'])
		shops_with_spells = sum(1 for s in self._shops.values() if s['spells'])
		shops_with_any = sum(1 for s in self._shops.values() if s['garrison'] or s['items'] or s['units'] or s['spells'])

		print(
			"\n",
			"="*78,
			"EXTRACTION STATISTICS",
			"="*78,
			"",
			f"Total shops:           {len(self._shops)}",
			f"Shops with content:    {shops_with_any}",
			f"  - With garrison:     {shops_with_garrison}",
			f"  - With items:        {shops_with_items}",
			f"  - With units:        {shops_with_units}",
			f"  - With spells:       {shops_with_spells}",
			"",
			f"Total products:        {total_products}",
			f"  - Garrison units:    {total_garrison}",
			f"  - Items:             {total_items}",
			f"  - Units:             {total_units}",
			f"  - Spells:            {total_spells}",
			sep="\n"
		)


if __name__ == '__main__':
	KBShopSaveExtractorCLI().run()
