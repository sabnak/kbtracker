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

	@abc.abstractmethod
	def sync(
		self,
		data: dict[str, dict[str, list[dict[str, Any]]]],
		profile_id: int
	) -> dict[str, int]:
		"""
		Sync parsed shop inventory data to database

		:param data:
			Parsed shop data from parse() method
		:param profile_id:
			Profile ID to associate inventories with
		:return:
			Dictionary with counts: {items: int, spells: int, units: int, garrison: int}
		:raises EntityNotFoundException:
			If any shop, item, spell, or unit not found in database
		"""
		...
