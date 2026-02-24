import pytest

from src.utils.parsers.game_data.KFSSpellsParser import KFSSpellsParser
from src.utils.parsers.game_data.KFSReader import KFSReader
from src.domain.game.entities.Localization import Localization
from src.core.Config import Config


class MockLocalizationRepository:
	"""Mock localization repository for testing"""

	def list_all(self, tag: str | None = None):
		all_localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_name',
				text='Dispel',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_dispell_hint',
				text='Removes all effects...',
				source='spells',
				tag='spells'
			),
			Localization(
				id=3,
				kb_id='spell_titan_sword_name',
				text='Titan Sword',
				source='spells',
				tag='spells'
			),
			Localization(
				id=4,
				kb_id='spell_titan_sword_hint',
				text='Summon the Titan Sword...',
				source='spells',
				tag='spells'
			),
			Localization(
				id=5,
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


class TestKFSSpellsParser:

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
		return KFSSpellsParser(
			reader=kfs_reader,
			localization_repository=mock_localization_repo
		)

	def test_parse_battle_spell_with_levels(self, parser):
		"""Test parsing dispell (battle spell) with levels block"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell']
		)

		assert len(raw_data_dict) == 1
		assert 'dispell' in raw_data_dict

		spell_data = raw_data_dict['dispell']

		# Verify basic fields
		assert spell_data['kb_id'] == 'dispell'
		assert spell_data['profit'] == 1
		assert spell_data['price'] == 2000
		assert spell_data['school'] == 1

		# Verify mana_cost and crystal_cost from levels block
		assert spell_data['mana_cost'] == [5, 5, 5]
		assert spell_data['crystal_cost'] == [1, 2, 5]

		# Verify data structure
		assert isinstance(spell_data['data'], dict)
		assert 'scripted' in spell_data['data']
		assert 'params' in spell_data['data']

	def test_parse_wandering_spell_without_levels(self, parser):
		"""Test parsing titan_sword (wandering spell) without levels block"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['titan_sword']
		)

		assert len(raw_data_dict) == 1
		assert 'titan_sword' in raw_data_dict

		spell_data = raw_data_dict['titan_sword']

		# Verify basic fields
		assert spell_data['kb_id'] == 'titan_sword'
		assert spell_data['profit'] == 4
		assert spell_data['price'] == 50000
		assert spell_data['school'] == 5

		# Verify mana_cost and crystal_cost are None (no levels block)
		assert spell_data['mana_cost'] is None
		assert spell_data['crystal_cost'] is None

		# Verify data structure
		assert isinstance(spell_data['data'], dict)

	def test_parse_all_spells_from_localization(self, parser):
		"""Test parsing all spells when no filter is provided"""
		raw_data_dict = parser.parse(game_name='Darkside_test')

		# Should find both dispell and titan_sword from mock localization
		assert len(raw_data_dict) == 2
		assert 'dispell' in raw_data_dict
		assert 'titan_sword' in raw_data_dict

	def test_parse_with_filter(self, parser):
		"""Test that allowed_kb_ids filter works correctly"""
		# Parse with specific filter
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell']
		)

		assert len(raw_data_dict) == 1
		assert 'dispell' in raw_data_dict
		assert raw_data_dict['dispell']['kb_id'] == 'dispell'

	def test_comma_separated_fields_split_to_lists(self, parser):
		"""Test that comma-separated params fields are split to lists"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell']
		)

		spell_data = raw_data_dict['dispell']
		params = spell_data['data']['params']

		# Verify exception field is split to list
		assert 'exception' in params
		assert isinstance(params['exception'], list)
		assert len(params['exception']) > 0
		assert 'effect_burn' in params['exception']
		assert 'effect_freeze' in params['exception']
		assert 'effect_poison' in params['exception']

		# Verify target field is split to list
		assert 'target' in params
		assert isinstance(params['target'], list)
		assert len(params['target']) == 3
		assert 'ally' in params['target']
		assert 'all' in params['target']

	def test_spell_kb_id_extraction_from_localization(self, parser):
		"""Test that spell kb_ids are correctly extracted from localization"""
		# The parser should extract kb_ids from 'spell_*' pattern
		raw_data_dict = parser.parse(game_name='Darkside_test')

		# All spells should have kb_id without 'spell_' prefix
		for kb_id, spell_data in raw_data_dict.items():
			assert not kb_id.startswith('spell_')
			assert not spell_data['kb_id'].startswith('spell_')

		assert 'dispell' in raw_data_dict
		assert 'titan_sword' in raw_data_dict

	def test_scripted_block_preserved(self, parser):
		"""Test that scripted block is preserved in data"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell']
		)

		spell_data = raw_data_dict['dispell']
		scripted = spell_data['data']['scripted']

		# Verify scripted block fields
		assert isinstance(scripted, dict)
		assert 'no_hint' in scripted
		assert 'script_attack' in scripted
		assert scripted['script_attack'] == 'spell_dispell_attack'

	def test_params_block_preserved(self, parser):
		"""Test that params block is preserved in data"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell']
		)

		spell_data = raw_data_dict['dispell']
		params = spell_data['data']['params']

		# Verify params block fields
		assert isinstance(params, dict)
		assert 'duration' in params
		assert params['duration'] == 0
		assert 'type' in params
		assert params['type'] == 'bonus'

	def test_multiple_spells_parsing(self, parser):
		"""Test parsing multiple spells at once"""
		raw_data_dict = parser.parse(
			game_name='Darkside_test',
			allowed_kb_ids=['dispell', 'titan_sword']
		)

		assert len(raw_data_dict) == 2

		# Verify battle spell
		assert raw_data_dict['dispell']['school'] == 1
		assert raw_data_dict['dispell']['mana_cost'] is not None
		assert raw_data_dict['dispell']['crystal_cost'] is not None

		# Verify wandering spell
		assert raw_data_dict['titan_sword']['school'] == 5
		assert raw_data_dict['titan_sword']['mana_cost'] is None
		assert raw_data_dict['titan_sword']['crystal_cost'] is None
