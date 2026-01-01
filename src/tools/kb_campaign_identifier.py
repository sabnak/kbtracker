#!/usr/bin/env python3
"""
King's Bounty Campaign Identifier CLI

CLI wrapper for CampaignIdentifierParser.
Extracts a composite campaign identifier from save files based on hero character names.

Author: Claude (Anthropic)
Date: December 31, 2025
Version: 2.0.0
"""
import sys
from pathlib import Path

from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller
from src.domain.game.parsers.save_data.ICampaignIdentifierParser import ICampaignIdentifierParser


def main():
	"""Main entry point"""
	if len(sys.argv) < 2:
		print("King's Bounty Campaign Identifier v2.0.0")
		print()
		print("Usage:")
		print(f"  python {sys.argv[0]} <save_data_file>")
		print()
		print("Arguments:")
		print("  save_data_file  Path to King's Bounty save 'data' file")
		print()
		print("Example:")
		print(f"  python {sys.argv[0]} path/to/save/1707078232/data")
		sys.exit(1)

	save_path = Path(sys.argv[1])

	if not save_path.exists():
		print(f"Error: File not found: {save_path}")
		sys.exit(1)

	try:
		container = Container()
		installer = DefaultInstaller(container)
		installer.install()
		container.wire(modules=[__name__])

		parser: ICampaignIdentifierParser = container.campaign_identifier_parser()
		result = parser.parse(save_path)

		print("=" * 60)
		print("CAMPAIGN IDENTIFIER EXTRACTION")
		print("=" * 60)
		print(f"\nSave file: {save_path}")
		print(f"\nHero name: {result['full_name']}")
		print(f"  First name:  {result['first_name']}")
		print(f"  Second name: {result['second_name']}")
		print(f"\nCampaign ID: {result['campaign_id']}")

	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)


if __name__ == '__main__':
	main()
