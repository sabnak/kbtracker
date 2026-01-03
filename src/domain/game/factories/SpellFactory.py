import re
from typing import Any

from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.LocEntity import LocEntity
from src.domain.game.entities.Spell import Spell
from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.ILocFactory import ILocFactory
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.ISpellFactory import ISpellFactory


class SpellFactory(ISpellFactory):

	@inject
	def __init__(
		self,
		loc_factory: ILocFactory = Provide[Container.loc_factory],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		"""
		Initialize spell factory

		:param loc_factory:
			Factory for creating LocEntity from localizations
		:param localization_repository:
			Repository for fetching localized text
		"""
		self._loc_factory = loc_factory
		self._localization_repository = localization_repository

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
		kb_id = raw_data['kb_id']
		school = SpellSchool(raw_data['school'])

		loc = self._fetch_loc(kb_id)

		return Spell(
			id=0,
			kb_id=kb_id,
			profit=raw_data['profit'],
			price=raw_data['price'],
			school=school,
			mana_cost=raw_data.get('mana_cost'),
			crystal_cost=raw_data.get('crystal_cost'),
			data=raw_data['data'],
			loc=loc
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

	def _fetch_loc(self, kb_id: str) -> LocEntity | None:
		"""
		Fetch localizations for spell and create LocEntity

		Pattern matches 'spell_{kb_id}_*' or exactly 'spell_{kb_id}'
		to avoid matching spell_empathy2 when looking for spell_empathy

		:param kb_id:
			Spell kb_id
		:return:
			LocEntity or None if no localizations found
		"""
		all_localizations = self._localization_repository.list_all()
		pattern = re.compile(rf'^spell_{re.escape(kb_id)}(?:_|$)')
		spell_localizations = [
			loc for loc in all_localizations
			if pattern.match(loc.kb_id)
		]

		if not spell_localizations:
			return None

		return self._loc_factory.create_from_localizations(spell_localizations)
