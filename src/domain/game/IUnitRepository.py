from abc import ABC, abstractmethod

from src.domain.game.entities.Unit import Unit


class IUnitRepository(ABC):

	@abstractmethod
	def create(self, unit: Unit) -> Unit:
		"""
		Create new unit

		:param unit:
			Unit to create
		:return:
			Created unit with ID
		"""
		pass

	@abstractmethod
	def create_batch(self, units: list[Unit]) -> list[Unit]:
		"""
		Create multiple units

		:param units:
			Units to create
		:return:
			Created units with IDs
		"""
		pass

	@abstractmethod
	def get_by_id(self, unit_id: int) -> Unit | None:
		"""
		Get unit by database ID

		:param unit_id:
			Unit ID
		:return:
			Unit or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> Unit | None:
		"""
		Get unit by game identifier

		:param kb_id:
			Game identifier
		:return:
			Unit or None if not found
		"""
		pass

	@abstractmethod
	def list_all(self, sort_by: str = "name", sort_order: str = "asc") -> list[Unit]:
		"""
		Get all units

		:param sort_by:
			Field to sort by (name, kb_id)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of all units
		"""
		pass

	@abstractmethod
	def search_by_name(self, query: str) -> list[Unit]:
		"""
		Search units by name (case-insensitive)

		:param query:
			Search query
		:return:
			List of matching units
		"""
		pass
