import pytest

from src.utils.parsers.game_data.KFSUnitParser import KFSUnitParser
from src.utils.parsers.game_data.KFSReader import KFSReader
from src.domain.game.entities.Localization import Localization
from src.domain.game.entities.UnitClass import UnitClass
from src.core.Config import Config


class MockLocalizationRepository:
	"""Mock localization repository for testing"""

	def list_all(self, tag: str | None = None):
		all_localizations = [
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
		if tag:
			return [loc for loc in all_localizations if loc.tag == tag]
		return all_localizations

	def get_by_kb_id(self, kb_id: str):
		all_localizations = self.list_all()
		for loc in all_localizations:
			if loc.kb_id == kb_id:
				return loc
		return None


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
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(raw_data_dict) == 1
		assert 'light_archdruid' in raw_data_dict

		unit_data = raw_data_dict['light_archdruid']

		# Verify basic fields
		assert unit_data['kb_id'] == 'light_archdruid'
		assert unit_data['unit_class'] == UnitClass.CHESSPIECE
		assert isinstance(unit_data['params'], dict)
		assert isinstance(unit_data['main'], dict)

		# Verify arena_params are present
		params = unit_data['params']
		assert 'race' in params
		assert params['race'] == 'elf'
		assert 'level' in params
		assert params['level'] == 4
		assert 'cost' in params
		assert params['cost'] == 3750

		# Verify features_hints is converted to list
		assert 'features_hints' in params
		assert isinstance(params['features_hints'], list)
		assert len(params['features_hints']) > 0
		assert 'stamina_header/stamina_2_hint' in params['features_hints']

		# Verify attacks is converted to list
		assert 'attacks' in params
		assert isinstance(params['attacks'], list)
		assert 'moveattack' in params['attacks']
		assert 'archdruid_rock' in params['attacks']

	def test_parse_light_archdruid(self, parser):
		"""Test parsing light_archdruid unit"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(raw_data_dict) == 1
		unit_data = raw_data_dict['light_archdruid']

		assert unit_data['kb_id'] == 'light_archdruid'
		assert unit_data['unit_class'] == UnitClass.CHESSPIECE
		assert unit_data['params']['race'] == 'elf'
		assert unit_data['params']['level'] == 4
		assert unit_data['params']['cost'] == 3750

		# Verify list conversions
		assert isinstance(unit_data['params']['features_hints'], list)
		assert isinstance(unit_data['params']['attacks'], list)

		# Verify specific attacks
		assert 'moveattack' in unit_data['params']['attacks']
		assert 'archdruid_rock' in unit_data['params']['attacks']
		assert 'archdruid_stone' in unit_data['params']['attacks']

	def test_parse_all_units_from_localization(self, parser):
		"""Test parsing all units when no filter is provided"""
		raw_data_dict = parser.parse(game_name='Darkside_test')

		# Should find both light_archdruid and bowman from mock localization
		assert len(raw_data_dict) == 2
		assert 'light_archdruid' in raw_data_dict
		assert 'bowman' in raw_data_dict

	def test_parse_with_filter(self, parser):
		"""Test that allowed_kb_ids filter works correctly"""
		# Parse with specific filter
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)

		assert len(raw_data_dict) == 1
		assert 'light_archdruid' in raw_data_dict
		assert raw_data_dict['light_archdruid']['kb_id'] == 'light_archdruid'

	def test_features_hints_parsing(self, parser):
		"""Test that features_hints is properly split"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit_data = raw_data_dict['light_archdruid']

		features = unit_data['params']['features_hints']
		# Each feature should be in format "header/hint"
		for feature in features:
			assert isinstance(feature, str)
			assert '/' in feature

	def test_attacks_parsing(self, parser):
		"""Test that attacks are properly split"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit_data = raw_data_dict['light_archdruid']

		attacks = unit_data['params']['attacks']
		# Should have multiple attacks
		assert len(attacks) >= 3
		# Each attack should be a string
		for attack in attacks:
			assert isinstance(attack, str)
			assert len(attack) > 0

	def test_resistances_preserved_as_dict(self, parser):
		"""Test that nested dicts like resistances are preserved"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['light_archdruid']
		)
		unit_data = raw_data_dict['light_archdruid']

		# Resistances should be a nested dict
		assert 'resistances' in unit_data['params']
		assert isinstance(unit_data['params']['resistances'], dict)
		assert 'physical' in unit_data['params']['resistances']
		assert 'poison' in unit_data['params']['resistances']
		assert 'magic' in unit_data['params']['resistances']

	def test_unit_kb_id_extraction_from_localization(self, parser):
		"""Test that unit kb_ids are correctly extracted from localization"""
		# The parser should extract kb_ids from 'cpn_*' pattern
		raw_data_dict = parser.parse(game_name='Darkside_test')

		# All units should have kb_id without 'cpn_' prefix
		for kb_id, unit_data in raw_data_dict.items():
			assert not kb_id.startswith('cpn_')
			assert not unit_data['kb_id'].startswith('cpn_')

		assert 'light_archdruid' in raw_data_dict
		assert 'bowman' in raw_data_dict

	def test_parse_bowman(self, parser):
		"""Test parsing bowman unit"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['bowman']
		)

		assert len(raw_data_dict) == 1
		unit_data = raw_data_dict['bowman']

		assert unit_data['kb_id'] == 'bowman'
		assert unit_data['unit_class'] == UnitClass.CHESSPIECE
		assert unit_data['params']['race'] == 'human'
		assert unit_data['params']['level'] == 2
		assert unit_data['params']['cost'] == 160

		# Verify list conversions
		assert isinstance(unit_data['params']['features_hints'], list)
		assert isinstance(unit_data['params']['attacks'], list)

		# Verify specific features and attacks
		assert 'stamina_header/stamina_3_hint' in unit_data['params']['features_hints']
		assert 'light_header/light_hint' in unit_data['params']['features_hints']
		assert 'shot_header/shot_bowman_hint' in unit_data['params']['features_hints']
		assert 'throw1' in unit_data['params']['attacks']
