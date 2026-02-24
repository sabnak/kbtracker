from abc import ABC, abstractmethod

from src.domain.game.entities.Spell import Spell
from src.domain.game.entities.SpellSchool import SpellSchool


class ISpellRepository(ABC):

	@abstractmethod
	def create(self, spell: Spell) -> Spell:
		"""
		Create new spell

		:param spell:
			Spell to create
		:return:
			Created spell with database ID
		"""
		pass

	@abstractmethod
	def create_batch(self, spells: list[Spell]) -> list[Spell]:
		"""
		Create multiple spells

		:param spells:
			Spells to create
		:return:
			Created spells with database IDs
		"""
		pass

	@abstractmethod
	def get_by_id(self, spell_id: int) -> Spell | None:
		"""
		Get spell by database ID

		:param spell_id:
			Spell ID
		:return:
			Spell or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id(self, kb_id: str) -> Spell | None:
		"""
		Get spell by game identifier

		:param kb_id:
			Game identifier
		:return:
			Spell or None if not found
		"""
		pass

	@abstractmethod
	def list_all(
		self,
		school: SpellSchool | None = None,
		sort_by: str = "name",
		sort_order: str = "asc"
	) -> list[Spell]:
		"""
		Get all spells, optionally filtered by school

		:param school:
			Optional spell school filter
		:param sort_by:
			Field to sort by (name, school, mana, crystal)
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			List of all spells (filtered and sorted)
		"""
		pass

	@abstractmethod
	def get_by_ids(self, ids: list[int]) -> dict[int, Spell]:
		"""
		Batch fetch spells by IDs

		:param ids:
			List of spell IDs
		:return:
			Dictionary mapping ID to Spell
		"""
		pass

	@abstractmethod
	def search_with_filters(
		self,
		school: SpellSchool | None = None,
		profit: int | None = None,
		sort_by: str = "name",
		sort_order: str = "asc",
		profile_id: int | None = None
	) -> list[Spell]:
		"""
		Search spells with filter criteria

		:param school:
			Optional spell school filter
		:param profit:
			Optional profit/rank filter (1-5)
		:param sort_by:
			Field to sort by (name, school, mana, crystal, profit)
		:param sort_order:
			Sort direction (asc, desc)
		:param profile_id:
			Optional profile ID filter (shows only spells in shop inventory for profile)
		:return:
			List of spells matching all provided criteria
		"""
		pass
