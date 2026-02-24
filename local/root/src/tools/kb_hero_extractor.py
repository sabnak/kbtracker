import argparse
import json
import sys
from pathlib import Path

import pydantic

from src.tools.CLITool import CLITool, T


class LaunchParams(pydantic.BaseModel):

	save_path: Path


class KBHeroSaveExtractorCLI(CLITool[LaunchParams]):

	def _build_params(self) -> T:
		p = argparse.ArgumentParser(description='King\'s Bounty Hero Extractor')
		p.add_argument('save_path', type=Path, help='Path to King\'s Bounty save name')
		args = p.parse_args()
		return LaunchParams(save_path=args.save_path)

	def _run(self):
		parser = self._container.hero_save_parser()

		if not self._launch_params.save_path.exists():
			print(f"Error: Save not found: {self._launch_params.save_path}")
			sys.exit(1)

		print(
			f"Input: {self._launch_params.save_path}",
			"Extracting hero data...",
			sep="\n"
		)

		result = parser.parse(self._launch_params.save_path)

		print(f"Result:", json.dumps(result, ensure_ascii=False), sep="\n")


if __name__ == '__main__':
	KBHeroSaveExtractorCLI().run()
