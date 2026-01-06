from abc import ABC, abstractmethod

from src.domain.game.entities.Unit import Unit


class IUnitFactory(ABC):

	@abstractmethod
	def create_from_raw_data(self, raw_data: dict[str, any]) -> Unit:
		"""
		Create Unit entity from raw parsed data with localization

		Processes attacks and features with localization lookups.
		Extracts explicit properties from params.

		:param raw_data:
			Dictionary with keys: kb_id, unit_class, main, params
		:return:
			Fully initialized Unit entity with id=0
		"""
		pass

	@abstractmethod
	def create_batch_from_raw_data(
		self,
		raw_data_dict: dict[str, dict[str, any]]
	) -> list[Unit]:
		"""
		Create multiple Unit entities from dictionary of raw data

		:param raw_data_dict:
			Dictionary mapping kb_id to raw unit data
		:return:
			List of Unit entities
		"""
		pass
