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
		with self._get_session() as session:
			query = session.query(SpellMapper)

			if school:
				query = query.filter(SpellMapper.school == school.value)

			# For name sorting, we need to sort by loc.name which is fetched separately
			# So we skip database sorting and sort in Python after fetching loc
			if sort_by != "name":
				query = self._apply_sorting(query, sort_by, sort_order)

			mappers = query.all()
			spells = [self._mapper_to_entity(m) for m in mappers]

			# Sort by localized name in Python if requested
			if sort_by == "name":
				spells.sort(
					key=lambda s: (s.loc.name.lower() if s.loc and s.loc.name else ""),
					reverse=(sort_order.lower() == "desc")
				)

			return spells

	def get_by_ids(self, ids: list[int]) -> dict[int, Spell]:
		"""
		Batch fetch spells by IDs

		:param ids:
			List of spell IDs
		:return:
			Dictionary mapping ID to Spell
		"""
		if not ids:
			return {}

		with self._get_session() as session:
			mappers = session.query(SpellMapper).filter(SpellMapper.id.in_(ids)).all()

			result = {}
			for mapper in mappers:
				spell = self._mapper_to_entity(mapper)
				result[spell.id] = spell

			return result

	def _apply_sorting(self, query, sort_by: str, sort_order: str):
		"""
		Apply ORDER BY clause to query

		:param query:
			SQLAlchemy query
		:param sort_by:
			Field to sort by
		:param sort_order:
			Sort direction (asc, desc)
		:return:
			Query with ORDER BY applied
		"""
		from sqlalchemy import desc, asc

		# Map sort fields to database columns
		# For arrays, use [1] to get first element (PostgreSQL arrays are 1-indexed)
		sort_column_map = {
			"name": SpellMapper.kb_id,
			"school": SpellMapper.school,
			"mana": SpellMapper.mana_cost[1],
			"crystal": SpellMapper.crystal_cost[1]
		}

		sort_column = sort_column_map.get(sort_by, SpellMapper.kb_id)

		if sort_order.lower() == "desc":
			return query.order_by(desc(sort_column))
		else:
			return query.order_by(asc(sort_column))

	def _fetch_loc(self, kb_id: str) -> LocStrings | None:
		"""
		Fetch localizations for spell and create LocStrings

		Pattern matches 'spell_{kb_id}_%' with escaped underscores
		This ensures we match spell_empathy_name but not spell_empathy2_name

		:param kb_id:
			Spell kb_id
		:return:
			LocStrings or None if no localizations found
		"""
		pattern = f"spell\\_{kb_id}\\_%"
		spell_localizations = self._localization_repository.search_by_kb_id(pattern, use_regex=False)

		if not spell_localizations:
			return None

		return self._loc_factory.create_from_localizations(spell_localizations)
