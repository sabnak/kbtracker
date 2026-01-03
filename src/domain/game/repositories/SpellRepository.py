import re

from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.Spell import Spell
from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.ILocFactory import ILocFactory
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.ISpellRepository import ISpellRepository
from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.game.repositories.mappers.SpellMapper import SpellMapper


class SpellRepository(CrudRepository[Spell, SpellMapper], ISpellRepository):

	@inject
	def __init__(
		self,
		loc_factory: ILocFactory = Provide[Container.loc_factory],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		"""
		Initialize spell repository

		:param loc_factory:
			Factory for creating LocStrings from localizations
		:param localization_repository:
			Repository for fetching localized text
		"""
		super().__init__()
		self._loc_factory = loc_factory
		self._localization_repository = localization_repository

	def _entity_to_mapper(self, entity: Spell) -> SpellMapper:
		"""
		Convert Spell entity to SpellMapper

		:param entity:
			Spell entity to convert
		:return:
			SpellMapper instance
		"""
		return SpellMapper(
			kb_id=entity.kb_id,
			profit=entity.profit,
			price=entity.price,
			school=entity.school.value,
			hide=entity.hide,
			mana_cost=entity.mana_cost,
			crystal_cost=entity.crystal_cost,
			data=entity.data
		)

	def _mapper_to_entity(self, mapper: SpellMapper) -> Spell:
		"""
		Convert SpellMapper to Spell entity

		Fetches localizations from repository and creates LocStrings

		:param mapper:
			SpellMapper to convert
		:return:
			Spell entity with populated loc field
		"""
		loc = self._fetch_loc(mapper.kb_id)

		return Spell(
			id=mapper.id,
			kb_id=mapper.kb_id,
			profit=mapper.profit,
			price=mapper.price,
			school=SpellSchool(mapper.school),
			hide=mapper.hide,
			mana_cost=mapper.mana_cost,
			crystal_cost=mapper.crystal_cost,
			data=mapper.data,
			loc=loc
		)

	def _get_entity_type_name(self) -> str:
		"""
		Get entity type name

		:return:
			Entity type name
		"""
		return "Spell"

	def _get_duplicate_identifier(self, entity: Spell) -> str:
		"""
		Get duplicate identifier for Spell

		:param entity:
			Spell entity
		:return:
			Identifier string
		"""
		return f"kb_id={entity.kb_id}"

	def create(self, spell: Spell) -> Spell:
		"""
		Create new spell

		:param spell:
			Spell entity to create
		:return:
			Created spell with database ID
		"""
		return self._create_single(spell)

	def create_batch(self, spells: list[Spell]) -> list[Spell]:
		"""
		Create multiple spells

		:param spells:
			List of spell entities to create
		:return:
			List of created spells with database IDs
		"""
		return self._create_batch(spells)

	def get_by_id(self, spell_id: int) -> Spell | None:
		"""
		Get spell by database ID

		:param spell_id:
			Spell ID
		:return:
			Spell or None if not found
		"""
		with self._get_session() as session:
			mapper = session.query(SpellMapper).filter(
				SpellMapper.id == spell_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> Spell | None:
		"""
		Get spell by game identifier

		:param kb_id:
			Game identifier
		:return:
			Spell or None if not found
		"""
		with self._get_session() as session:
			mapper = session.query(SpellMapper).filter(
				SpellMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self, school: SpellSchool | None = None) -> list[Spell]:
		"""
		Get all spells, optionally filtered by school

		:param school:
			Optional spell school filter
		:return:
			List of all spells (filtered if school provided)
		"""
		with self._get_session() as session:
			query = session.query(SpellMapper)

			if school:
				query = query.filter(SpellMapper.school == school.value)

			mappers = query.all()
			return [self._mapper_to_entity(m) for m in mappers]

	def _fetch_loc(self, kb_id: str) -> LocStrings | None:
		"""
		Fetch localizations for spell and create LocStrings

		Pattern matches 'spell_{kb_id}_*' or exactly 'spell_{kb_id}'
		to avoid matching spell_empathy2 when looking for spell_empathy

		:param kb_id:
			Spell kb_id
		:return:
			LocStrings or None if no localizations found
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
