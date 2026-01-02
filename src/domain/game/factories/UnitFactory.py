from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitMovetype import UnitMovetype
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.IUnitFactory import IUnitFactory
from src.domain.game.factories.UnitAttacksProcessor import UnitAttacksProcessor
from src.domain.game.factories.UnitFeaturesProcessor import UnitFeaturesProcessor


class UnitFactory(IUnitFactory):

	@inject
	def __init__(
		self,
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		"""
		Initialize unit factory

		:param localization_repository:
			Repository for fetching localized text
		"""
		self._localization_repository = localization_repository
		self._attacks_processor = UnitAttacksProcessor(localization_repository)
		self._features_processor = UnitFeaturesProcessor(localization_repository)

	def create_from_raw_data(self, raw_data: dict[str, any]) -> Unit:
		"""
		Create Unit entity from raw parsed data

		:param raw_data:
			Dictionary with keys: kb_id, unit_class, main, params
		:return:
			Unit entity with id=0
		"""
		kb_id = raw_data['kb_id']
		unit_class = raw_data['unit_class']
		main = raw_data['main']
		params = raw_data['params']

		name = self._fetch_name(kb_id)
		attacks = self._attacks_processor.process(params)
		features = self._features_processor.process(params)
		movetype = UnitMovetype(params['movetype']) if params.get('movetype') is not None else None

		return Unit(
			id=0,
			kb_id=kb_id,
			name=name,
			unit_class=unit_class,
			main=main,
			params=params,
			cost=params.get('cost'),
			krit=params.get('krit'),
			race=params.get('race'),
			level=params.get('level'),
			speed=params.get('speed'),
			attack=params.get('attack'),
			defense=params.get('defense'),
			hitback=params.get('hitback'),
			hitpoint=params.get('hitpoint'),
			movetype=movetype,
			defenseup=params.get('defenseup'),
			initiative=params.get('initiative'),
			leadership=params.get('leadership'),
			resistance=params.get('resistances'),
			features=features,
			attacks=attacks
		)

	def create_batch_from_raw_data(
		self,
		raw_data_dict: dict[str, dict[str, any]]
	) -> list[Unit]:
		"""
		Create multiple units from dictionary

		:param raw_data_dict:
			Dictionary mapping kb_id to raw data
		:return:
			List of Unit entities
		"""
		units = []
		for kb_id, raw_data in raw_data_dict.items():
			unit = self.create_from_raw_data(raw_data)
			units.append(unit)
		return units

	def _fetch_name(self, kb_id: str) -> str:
		"""
		Fetch unit name from localization repository

		:param kb_id:
			Unit kb_id
		:return:
			Localized unit name or kb_id if not found
		"""
		localization_kb_id = f'cpn_{kb_id}'
		localization = self._localization_repository.get_by_kb_id(localization_kb_id)
		return localization.text if localization else kb_id
