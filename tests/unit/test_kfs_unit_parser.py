import pytest

from src.utils.parsers.game_data.KFSUnitParser import KFSUnitParser
from src.utils.parsers.game_data.KFSReader import KFSReader
from src.domain.game.entities.Localization import Localization
from src.domain.game.entities.UnitClass import UnitClass
from src.core.Config import Config


class MockLocalizationRepository:
	"""Mock localization repository for testing"""

	def list_all(self):
		return [
			Localization(
				id=1,
				kb_id='cpn_light_archdruid',
				text='Light Archdruid',
				source='units',
				tag='units'
			),
			Localization(
				id=2,
				kb_id='cpn_bowman',
				text='Bowman',
				source='units',
				tag='units'
			),
			Localization(
				id=3,
				kb_id='itm_some_item',
				text='Some Item',
				source='items',
				tag='items'
			)
		]


class TestKFSUnitParser:

	@pytest.fixture
	def test_config(self):
		"""Create test config pointing to test data"""
		config = Config()
		config.tmp_dir = "/app/tests/game_files/tests/tmp_persist"
		return config

	@pytest.fixture
	def kfs_reader(self, test_config):
		"""Create KFSReader with test config"""
		return KFSReader(config=test_config)

	@pytest.fixture
	def mock_localization_repo(self):
		"""Create mock localization repository"""
		return MockLocalizationRepository()

	@pytest.fixture
	def parser(self, kfs_reader, mock_localization_repo):
		"""Create parser with test dependencies"""
		return KFSUnitParser(
			reader=kfs_reader,
			localization_repository=mock_localization_repo
		)

	def test_parse_light_archdruid_full(self, parser):
		"""Test parsing light_archdruid unit with full verification"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(units) == 1
		unit = units[0]

		# Verify basic fields
		assert unit.kb_id == 'light_archdruid'
		assert unit.id == 0
		assert unit.name == ''
		assert unit.unit_class == UnitClass.CHESSPIECE
		assert isinstance(unit.params, dict)

		# Verify arena_params are present
		assert 'race' in unit.params
		assert unit.params['race'] == 'elf'
		assert 'level' in unit.params
		assert unit.params['level'] == 4
		assert 'cost' in unit.params
		assert unit.params['cost'] == 3750

		# Verify features_hints is converted to list
		assert 'features_hints' in unit.params
		assert isinstance(unit.params['features_hints'], list)
		assert len(unit.params['features_hints']) > 0
		assert 'stamina_header/stamina_2_hint' in unit.params['features_hints']

		# Verify attacks is converted to list
		assert 'attacks' in unit.params
		assert isinstance(unit.params['attacks'], list)
		assert 'moveattack' in unit.params['attacks']
		assert 'archdruid_rock' in unit.params['attacks']

	def test_parse_light_archdruid(self, parser):
		"""Test parsing light_archdruid unit"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(units) == 1
		unit = units[0]

		assert unit.kb_id == 'light_archdruid'
		assert unit.unit_class == UnitClass.CHESSPIECE
		assert unit.params['race'] == 'elf'
		assert unit.params['level'] == 4
		assert unit.params['cost'] == 3750

		# Verify list conversions
		assert isinstance(unit.params['features_hints'], list)
		assert isinstance(unit.params['attacks'], list)

		# Verify specific attacks
		assert 'moveattack' in unit.params['attacks']
		assert 'archdruid_rock' in unit.params['attacks']
		assert 'archdruid_stone' in unit.params['attacks']

	def test_parse_all_units_from_localization(self, parser):
		"""Test parsing all units when no filter is provided"""
		units = parser.parse(game_name='Darkside_test')

		# Should find both light_archdruid and bowman from mock localization
		assert len(units) == 2
		unit_kb_ids = [unit.kb_id for unit in units]
		assert 'light_archdruid' in unit_kb_ids
		assert 'bowman' in unit_kb_ids

	def test_parse_with_filter(self, parser):
		"""Test that allowed_kb_ids filter works correctly"""
		# Parse with specific filter
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(units) == 1
		assert units[0].kb_id == 'light_archdruid'

	def test_features_hints_parsing(self, parser):
		"""Test that features_hints is properly split"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit = units[0]

		features = unit.params['features_hints']
		# Each feature should be in format "header/hint"
		for feature in features:
			assert isinstance(feature, str)
			assert '/' in feature

	def test_attacks_parsing(self, parser):
		"""Test that attacks are properly split"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit = units[0]

		attacks = unit.params['attacks']
		# Should have multiple attacks
		assert len(attacks) >= 3
		# Each attack should be a string
		for attack in attacks:
			assert isinstance(attack, str)
			assert len(attack) > 0

	def test_resistances_preserved_as_dict(self, parser):
		"""Test that nested dicts like resistances are preserved"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit = units[0]

		# Resistances should be a nested dict
		assert 'resistances' in unit.params
		assert isinstance(unit.params['resistances'], dict)
		assert 'physical' in unit.params['resistances']
		assert 'poison' in unit.params['resistances']
		assert 'magic' in unit.params['resistances']

	def test_unit_kb_id_extraction_from_localization(self, parser):
		"""Test that unit kb_ids are correctly extracted from localization"""
		# The parser should extract kb_ids from 'cpn_*' pattern
		units = parser.parse(game_name='Darkside_test')

		# All units should have kb_id without 'cpn_' prefix
		for unit in units:
			assert not unit.kb_id.startswith('cpn_')

		unit_kb_ids = [unit.kb_id for unit in units]
		assert 'light_archdruid' in unit_kb_ids
		assert 'bowman' in unit_kb_ids

	def test_parse_bowman(self, parser):
		"""Test parsing bowman unit"""
		units = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['bowman']
		)

		assert len(units) == 1
		unit = units[0]

		assert unit.kb_id == 'bowman'
		assert unit.unit_class == UnitClass.CHESSPIECE
		assert unit.params['race'] == 'human'
		assert unit.params['level'] == 2
		assert unit.params['cost'] == 160

		# Verify list conversions
		assert isinstance(unit.params['features_hints'], list)
		assert isinstance(unit.params['attacks'], list)

		# Verify specific features and attacks
		assert 'stamina_header/stamina_3_hint' in unit.params['features_hints']
		assert 'light_header/light_hint' in unit.params['features_hints']
		assert 'shot_header/shot_bowman_hint' in unit.params['features_hints']
		assert 'throw1' in unit.params['attacks']
