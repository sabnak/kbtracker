import abc
from pathlib import Path
from typing import Any


class IShopInventoryParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, save_path: Path) -> list[dict[str, Any]]:
		"""
		Extract shop inventory data from save file

		:param save_path:
			Path to save 'data' file
		:return:
			List of shop dictionaries with structure:
			[
				{
					"itext": str,      # Shop itext ID or empty string
					"actor": str,      # Actor ID or empty string
					"location": str,   # Location name (e.g., "m_portland", "dragondor")
					"inventory": {
						"garrison": list[dict],
						"items": list[dict],
						"units": list[dict],
						"spells": list[dict]
					}
				},
				...
			]
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
