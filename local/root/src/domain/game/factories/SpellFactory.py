from typing import Any

from src.domain.game.entities.Spell import Spell
from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.interfaces.ISpellFactory import ISpellFactory


class SpellFactory(ISpellFactory):

	def create_from_raw_data(self, raw_data: dict[str, Any]) -> Spell:
		"""
		Create Spell entity from raw parsed data

		:param raw_data:
			Dictionary with keys: kb_id, profit, price, school,
			mana_cost (optional), crystal_cost (optional), data
		:return:
			Fully initialized Spell entity with id=0
		"""
		kb_id = raw_data['kb_id']
		school = SpellSchool(raw_data['school'])

		return Spell(
			id=0,
			kb_id=kb_id,
			profit=raw_data['profit'],
			price=raw_data['price'],
			school=school,
			mana_cost=raw_data.get('mana_cost'),
			crystal_cost=raw_data.get('crystal_cost'),
			data=raw_data['data'],
			loc=None
		)

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
		spells = []
		for kb_id, raw_data in raw_data_dict.items():
			spell = self.create_from_raw_data(raw_data)
			spells.append(spell)
		return spells
