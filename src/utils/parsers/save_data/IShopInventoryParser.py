import abc
from pathlib import Path
from typing import Any


class IShopInventoryParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, save_path: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
		"""
		Extract shop inventory data from save file

		:param save_path:
			Path to save 'data' file
		:return:
			Dictionary mapping shop_id to inventory sections
			Format: {shop_id: {garrison: [...], items: [...], units: [...], spells: [...]}}
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
