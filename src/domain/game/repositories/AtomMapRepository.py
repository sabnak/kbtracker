from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.IAtomMapRepository import IAtomMapRepository
from src.domain.game.ILocFactory import ILocFactory
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.repositories.CrudRepository import CrudRepository
from src.domain.game.repositories.mappers.AtomMapMapper import AtomMapMapper


class AtomMapRepository(CrudRepository[AtomMap, AtomMapMapper], IAtomMapRepository):

	@inject
	def __init__(
		self,
		loc_factory: ILocFactory = Provide[Container.loc_factory],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		super().__init__()
		self._loc_factory = loc_factory
		self._localization_repository = localization_repository

	def _entity_to_mapper(self, entity: AtomMap) -> AtomMapMapper:
		return AtomMapMapper(
			kb_id=entity.kb_id
		)

	def _mapper_to_entity(self, mapper: AtomMapMapper) -> AtomMap:
		loc = self._fetch_loc(mapper.kb_id)

		return AtomMap(
			id=mapper.id,
			kb_id=mapper.kb_id,
			loc=loc
		)

	def _get_entity_type_name(self) -> str:
		return "AtomMap"

	def _get_duplicate_identifier(self, entity: AtomMap) -> str:
		return f"kb_id={entity.kb_id}"

	def create(self, atom_map: AtomMap) -> AtomMap:
		return self._create_single(atom_map)

	def create_batch(self, atom_maps: list[AtomMap]) -> list[AtomMap]:
		return self._create_batch(atom_maps)

	def get_by_id(self, atom_map_id: int) -> AtomMap | None:
		with self._get_session() as session:
			mapper = session.query(AtomMapMapper).filter(
				AtomMapMapper.id == atom_map_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def get_by_kb_id(self, kb_id: str) -> AtomMap | None:
		with self._get_session() as session:
			mapper = session.query(AtomMapMapper).filter(
				AtomMapMapper.kb_id == kb_id
			).first()
			return self._mapper_to_entity(mapper) if mapper else None

	def list_all(self) -> list[AtomMap]:
		with self._get_session() as session:
			mappers = session.query(AtomMapMapper).all()
			return [self._mapper_to_entity(m) for m in mappers]

	def get_by_ids(self, ids: list[int]) -> dict[int, AtomMap]:
		"""
		Batch fetch atom maps by IDs

		:param ids:
			List of atom map IDs
		:return:
			Dictionary mapping ID to AtomMap
		"""
		if not ids:
			return {}

		with self._get_session() as session:
			mappers = session.query(AtomMapMapper).filter(AtomMapMapper.id.in_(ids)).all()

			result = {}
			for mapper in mappers:
				atom_map = self._mapper_to_entity(mapper)
				result[atom_map.id] = atom_map

			return result

	def _fetch_loc(self, kb_id: str) -> LocStrings | None:
		pattern = f"itext\\_{kb_id}\\_%"
		localizations = self._localization_repository.search_by_kb_id(pattern, use_regex=False)

		if not localizations:
			return None

		return self._loc_factory.create_from_localizations(localizations)
