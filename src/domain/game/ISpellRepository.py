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
	def list_all(self, school: SpellSchool | None = None) -> list[Spell]:
		"""
		Get all spells, optionally filtered by school

		:param school:
			Optional spell school filter
		:return:
			List of all spells (filtered if school provided)
		"""
		pass
