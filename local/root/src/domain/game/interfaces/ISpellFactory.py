from abc import ABC, abstractmethod
from typing import Any

from src.domain.game.entities.Spell import Spell


class ISpellFactory(ABC):

	@abstractmethod
	def create_from_raw_data(self, raw_data: dict[str, Any]) -> Spell:
		"""
		Create Spell entity from raw parsed data with localization

		Fetches localizations from repository and enriches spell entity with loc data.

		:param raw_data:
			Dictionary with keys: kb_id, profit, price, school,
			mana_cost (optional), crystal_cost (optional), data
		:return:
			Fully initialized Spell entity with id=0 and populated loc field
		"""
		pass

	@abstractmethod
	def create_batch_from_raw_data(
		self,
		raw_data_dict: dict[str, dict[str, Any]]
	) -> list[Spell]:
		"""
		Create multiple Spell entities from dictionary of raw data

		:param raw_data_dict:
			Dictionary mapping kb_id to raw spell data
		:return:
			List of Spell entities
		"""
		pass
