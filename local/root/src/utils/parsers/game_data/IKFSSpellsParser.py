import abc
from typing import Any


class IKFSSpellsParser(abc.ABC):

	@abc.abstractmethod
	def parse(
		self,
		game_name: str,
		allowed_kb_ids: list[str] | None = None
	) -> dict[str, dict[str, Any]]:
		"""
		Extract and parse spell data from game files

		Returns dictionary: {kb_id: {kb_id, profit, price, school,
		                     mana_cost, crystal_cost, data}}

		Battle spells (school 1-4):
		- Have 'levels' block with mana/crystal costs
		- mana_cost and crystal_cost are lists [mana1, mana2, mana3]

		Wandering spells (school 5):
		- Have 'action' field instead of 'levels'
		- mana_cost and crystal_cost are None

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:param allowed_kb_ids:
			Optional list of spell kb_ids to parse (for testing)
		:return:
			Dictionary mapping kb_id to raw spell data
		:raises FileNotFoundError:
			When spell file not found
		:raises ValueError:
			When spell file has invalid structure
		"""
		...
