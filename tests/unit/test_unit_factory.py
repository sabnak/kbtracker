import pytest

from src.domain.game.entities.Unit import Unit
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.entities.UnitMovetype import UnitMovetype
from src.domain.game.entities.Localization import Localization
from src.domain.game.factories.UnitFactory import UnitFactory


class MockLocalizationRepository:
	"""Mock localization repository for testing"""

	def get_by_kb_id(self, kb_id: str):
		localizations = {
			'cpn_miner2': Localization(
				id=1,
				kb_id='cpn_miner2',
				text='Peasant',
				source='units',
				tag='units'
			),
			'cpn_light_archdruid': Localization(
				id=2,
				kb_id='cpn_light_archdruid',
				text='Light Archdruid',
				source='units',
				tag='units'
			),
			'archdruid_rock_hint': Localization(
				id=3,
				kb_id='archdruid_rock_hint',
				text='Rock attack hint text',
				source='attacks',
				tag='attacks'
			),
			'archdruid_rock_name': Localization(
				id=4,
				kb_id='archdruid_rock_name',
				text='Rock Attack',
				source='attacks',
				tag='attacks'
			),
			'stamina_header': Localization(
				id=5,
				kb_id='stamina_header',
				text='Stamina',
				source='features',
				tag='features'
			),
			'stamina_2_hint': Localization(
				id=6,
				kb_id='stamina_2_hint',
				text='Stamina level 2 hint',
				source='features',
				tag='features'
			)
		}
		return localizations.get(kb_id)


class TestUnitFactory:

	@pytest.fixture
	def mock_localization_repo(self):
		"""Create mock localization repository"""
		return MockLocalizationRepository()

	@pytest.fixture
	def factory(self, mock_localization_repo):
		"""Create factory with test dependencies"""
		return UnitFactory(localization_repository=mock_localization_repo)

	def test_create_from_raw_data_basic(self, factory):
		"""Test basic entity creation from raw data"""
		raw_data = {
			'kb_id': 'miner2',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {'some': 'data'},
			'params': {
				'cost': 100,
				'krit': 5,
				'race': 'human',
				'level': 1,
				'speed': 3,
				'attack': 10,
				'defense': 5,
				'hitback': 3,
				'hitpoint': 50,
				'movetype': 1,
				'defenseup': 2,
				'initiative': 1,
				'leadership': 0,
				'resistances': {
					'physical': 10,
					'magic': 5
				}
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.id == 0
		assert unit.kb_id == 'miner2'
		assert unit.name == 'Peasant'
		assert unit.unit_class == UnitClass.CHESSPIECE
		assert unit.cost == 100
		assert unit.krit == 5
		assert unit.race == 'human'
		assert unit.level == 1
		assert unit.speed == 3
		assert unit.attack == 10
		assert unit.defense == 5
		assert unit.hitback == 3
		assert unit.hitpoint == 50
		assert unit.movetype == UnitMovetype.SOARING
		assert unit.defenseup == 2
		assert unit.initiative == 1
		assert unit.leadership == 0
		assert unit.resistance == {'physical': 10, 'magic': 5}

	def test_create_with_name_fallback(self, factory):
		"""Test that kb_id is used when localization is missing"""
		raw_data = {
			'kb_id': 'unknown_unit',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.name == 'unknown_unit'

	def test_create_with_attacks(self, factory):
		"""Test attacks processing with localization"""
		raw_data = {
			'kb_id': 'light_archdruid',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'archdruid_rock': {
					'hint': 'archdruid_rock_hint',
					'power': 100,
					'radius': 2
				},
				'some_other_param': 'not an attack'
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.attacks is not None
		assert 'archdruid_rock' in unit.attacks
		attack = unit.attacks['archdruid_rock']
		assert attack['name'] == 'Rock Attack'
		assert attack['hint'] == 'Rock attack hint text'
		assert 'data' in attack
		assert attack['data']['power'] == 100
		assert attack['data']['radius'] == 2

	def test_create_with_attacks_fallback(self, factory):
		"""Test attacks processing with missing localization fallback"""
		raw_data = {
			'kb_id': 'light_archdruid',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'unknown_attack': {
					'hint': 'unknown_hint',
					'power': 50
				}
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.attacks is not None
		assert 'unknown_attack' in unit.attacks
		attack = unit.attacks['unknown_attack']
		assert attack['name'] == 'unknown_name'
		assert attack['hint'] == 'unknown_hint'

	def test_create_with_features(self, factory):
		"""Test features processing with localization"""
		raw_data = {
			'kb_id': 'light_archdruid',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'features_hints': [
					'stamina_header/stamina_2_hint'
				]
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.features is not None
		assert 'stamina_header/stamina_2_hint' in unit.features
		feature = unit.features['stamina_header/stamina_2_hint']
		assert feature['name'] == 'Stamina'
		assert feature['hint'] == 'Stamina level 2 hint'

	def test_create_with_features_fallback(self, factory):
		"""Test features processing with missing localization fallback"""
		raw_data = {
			'kb_id': 'light_archdruid',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'features_hints': [
					'unknown_header/unknown_hint'
				]
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.features is not None
		assert 'unknown_header/unknown_hint' in unit.features
		feature = unit.features['unknown_header/unknown_hint']
		assert feature['name'] == 'unknown_header'
		assert feature['hint'] == 'unknown_hint'

	def test_create_with_no_attacks(self, factory):
		"""Test that units without attacks have None"""
		raw_data = {
			'kb_id': 'miner2',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'cost': 100,
				'race': 'human'
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.attacks is None

	def test_create_with_no_features(self, factory):
		"""Test that units without features have None"""
		raw_data = {
			'kb_id': 'miner2',
			'unit_class': UnitClass.CHESSPIECE,
			'main': {},
			'params': {
				'cost': 100,
				'race': 'human'
			}
		}

		unit = factory.create_from_raw_data(raw_data)

		assert unit.features is None

	def test_create_batch_from_raw_data(self, factory):
		"""Test batch creation from dictionary"""
		raw_data_dict = {
			'miner2': {
				'kb_id': 'miner2',
				'unit_class': UnitClass.CHESSPIECE,
				'main': {},
				'params': {'cost': 100}
			},
			'light_archdruid': {
				'kb_id': 'light_archdruid',
				'unit_class': UnitClass.CHESSPIECE,
				'main': {},
				'params': {'cost': 3750}
			}
		}

		units = factory.create_batch_from_raw_data(raw_data_dict)

		assert len(units) == 2
		assert units[0].kb_id == 'miner2'
		assert units[0].name == 'Peasant'
		assert units[1].kb_id == 'light_archdruid'
		assert units[1].name == 'Light Archdruid'
