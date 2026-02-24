import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pydantic

from src.tools.CLITool import CLITool, T
from src.utils.parsers.save_data.SaveFileData import SaveFileData


class LaunchParams(pydantic.BaseModel):

	save_path: Path


class KBShopSaveExtractorCLI(CLITool[LaunchParams]):

	_result: SaveFileData | None = None
	_boundary = "=" * 78

	def _build_params(self) -> T:
		p = argparse.ArgumentParser(description='King\'s Bounty Shop Extractor')
		p.add_argument('save_path', type=Path, help='Path to King\'s Bounty save name')
		args = p.parse_args()
		return LaunchParams(save_path=args.save_path)

	def _run(self):
		self._result = None
		parser = self._container.save_data_parser()

		if not self._launch_params.save_path.exists():
			print(f"Error: Save not found: {self._launch_params.save_path}")
			sys.exit(1)

		save_name = self._launch_params.save_path.name
		output_dir = Path('/tmp/save_export')
		output_dir.mkdir(parents=True, exist_ok=True)
		output_path = output_dir / f'{save_name}.json'

		print(
			self._boundary,
			"KING'S BOUNTY SHOP EXTRACTOR",
			self._boundary,
			f"Input:  {self._launch_params.save_path}",
			f"Output: {output_path}\n",
			"Extracting shop data...",
			sep="\n"
		)

		self._result = parser.parse(self._launch_params.save_path)

		print("\nSaving to JSON...")
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(self._result.model_dump(), f, indent=2, ensure_ascii=False)

		self._print_statistics()

		print(
			"",
			self._boundary,
			f"SUCCESS: Extracted {len(self._result.shops)} shops to {output_path}",
			self._boundary,
			sep="\n"
		)

	def _print_statistics(self) -> None:
		summary = Counter()
		not_empty_shops = Counter()
		for shop in self._result.shops:
			inventory = shop['inventory']
			if inventory['garrison']:
				not_empty_shops['garrison'] += 1
				summary['garrison'] += len(inventory['garrison'])
			if inventory['items']:
				not_empty_shops['items'] += 1
				summary['items'] += len(inventory['items'])
			if inventory['units']:
				not_empty_shops['units'] += 1
				summary['units'] += len(inventory['units'])
			if inventory['spells']:
				not_empty_shops['spells'] += 1
				summary['spells'] += len(inventory['spells'])

		print(
			"\n",
			"="*78,
			"EXTRACTION STATISTICS",
			"="*78,
			"",
			f"Total shops:           {len(self._result.shops)}",
			f"  - With garrison:     {not_empty_shops['garrison']}",
			f"  - With items:        {not_empty_shops['items']}",
			f"  - With units:        {not_empty_shops['units']}",
			f"  - With spells:       {not_empty_shops['spells']}",
			"",
			f"Total products:        {summary['garrison'] + summary['items'] + summary['units'] + summary['spells']}",
			f"  - Garrison units:    {summary['garrison']}",
			f"  - Items:             {summary['items']}",
			f"  - Units:             {summary['units']}",
			f"  - Spells:            {summary['spells']}",
			"",
			f"Items in inventory: {len(self._result.hero_inventory.items) if self._result.hero_inventory else 0}",
			sep="\n"
		)


if __name__ == '__main__':
	KBShopSaveExtractorCLI().run()
