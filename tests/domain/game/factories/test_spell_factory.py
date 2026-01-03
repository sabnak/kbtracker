import pytest

from src.domain.game.entities.Localization import Localization
from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.factories.SpellFactory import SpellFactory
from src.domain.game.factories.LocFactory import LocFactory


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
				text='Removes all effects from target unit',
				source='spells',
				tag='spells'
			),
			Localization(
				id=3,
				kb_id='spell_dispell_desc',
				text='This spell removes all magical effects',
				source='spells',
				tag='spells'
			),
			Localization(
				id=4,
				kb_id='spell_dispell_header',
				text='Order Magic',
				source='spells',
				tag='spells'
			),
			Localization(
				id=5,
				kb_id='spell_titan_sword_name',
				text='Titan Sword',
				source='spells',
				tag='spells'
			),
			Localization(
				id=6,
				kb_id='spell_titan_sword_hint',
				text='Summon the legendary Titan Sword',
				source='spells',
				tag='spells'
			),
			Localization(
				id=7,
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


class TestSpellFactory:

	@pytest.fixture
	def mock_localization_repo(self):
		"""Create mock localization repository"""
		return MockLocalizationRepository()

	@pytest.fixture
	def loc_factory(self):
		"""Create LocFactory"""
		return LocFactory()

	@pytest.fixture
	def factory(self, loc_factory, mock_localization_repo):
		"""Create factory with test dependencies"""
		return SpellFactory(
			loc_factory=loc_factory,
			localization_repository=mock_localization_repo
		)

	def test_create_battle_spell_from_raw_data(self, factory):
		"""Test creating battle spell with levels from raw data"""
		raw_data = {
			'kb_id': 'dispell',
			'profit': 1,
			'price': 2000,
			'school': 1,
			'mana_cost': [5, 5, 5],
			'crystal_cost': [1, 2, 5],
			'data': {
				'scripted': {
					'no_hint': 1,
					'script_attack': 'spell_dispell_attack'
				},
				'params': {
					'duration': 0,
					'type': 'bonus',
					'exception': ['effect_burn', 'effect_freeze'],
					'target': ['ally', 'all', 'all']
				}
			}
		}

		spell = factory.create_from_raw_data(raw_data)

		assert spell.id == 0
		assert spell.kb_id == 'dispell'
		assert spell.profit == 1
		assert spell.price == 2000
		assert spell.school == SpellSchool.ORDER
		assert spell.mana_cost == [5, 5, 5]
		assert spell.crystal_cost == [1, 2, 5]
		assert isinstance(spell.data, dict)
		assert 'scripted' in spell.data
		assert 'params' in spell.data

	def test_create_wandering_spell_from_raw_data(self, factory):
		"""Test creating wandering spell without levels from raw data"""
		raw_data = {
			'kb_id': 'titan_sword',
			'profit': 4,
			'price': 50000,
			'school': 5,
			'mana_cost': None,
			'crystal_cost': None,
			'data': {
				'action': 'advspell_titan_sword',
				'category': 's'
			}
		}

		spell = factory.create_from_raw_data(raw_data)

		assert spell.id == 0
		assert spell.kb_id == 'titan_sword'
		assert spell.profit == 4
		assert spell.price == 50000
		assert spell.school == SpellSchool.WANDERING
		assert spell.mana_cost is None
		assert spell.crystal_cost is None
		assert isinstance(spell.data, dict)

	def test_spell_school_enum_conversion(self, factory):
		"""Test that school integer is converted to SpellSchool enum"""
		test_cases = [
			(1, SpellSchool.ORDER),
			(2, SpellSchool.CHAOS),
			(3, SpellSchool.DISTORTION),
			(4, SpellSchool.MIND),
			(5, SpellSchool.WANDERING)
		]

		for school_int, expected_enum in test_cases:
			raw_data = {
				'kb_id': 'test_spell',
				'profit': 1,
				'price': 1000,
				'school': school_int,
				'data': {}
			}

			spell = factory.create_from_raw_data(raw_data)
			assert spell.school == expected_enum

	def test_loc_enrichment_with_all_fields(self, factory):
		"""Test that loc is populated with all localization fields"""
		raw_data = {
			'kb_id': 'dispell',
			'profit': 1,
			'price': 2000,
			'school': 1,
			'mana_cost': [5, 5, 5],
			'crystal_cost': [1, 2, 5],
			'data': {}
		}

		spell = factory.create_from_raw_data(raw_data)

		assert spell.loc is not None
		assert spell.loc.name == 'Dispel'
		assert spell.loc.hint == 'Removes all effects from target unit'
		assert spell.loc.desc == 'This spell removes all magical effects'
		assert spell.loc.header == 'Order Magic'
		assert isinstance(spell.loc.texts, dict)
		assert len(spell.loc.texts) == 4

	def test_loc_enrichment_with_partial_fields(self, factory):
		"""Test that loc is populated with partial localization fields"""
		raw_data = {
			'kb_id': 'titan_sword',
			'profit': 4,
			'price': 50000,
			'school': 5,
			'data': {}
		}

		spell = factory.create_from_raw_data(raw_data)

		# titan_sword has name and hint but no desc or header
		assert spell.loc is not None
		assert spell.loc.name == 'Titan Sword'
		assert spell.loc.hint == 'Summon the legendary Titan Sword'
		assert spell.loc.desc is None
		assert spell.loc.header is None
		assert isinstance(spell.loc.texts, dict)
		assert len(spell.loc.texts) == 2

	def test_loc_fallback_when_no_localizations(self, factory):
		"""Test that loc is None when no localizations are found"""
		raw_data = {
			'kb_id': 'unknown_spell',
			'profit': 1,
			'price': 1000,
			'school': 1,
			'data': {}
		}

		spell = factory.create_from_raw_data(raw_data)

		assert spell.loc is None

	def test_create_batch_from_raw_data(self, factory):
		"""Test batch creation from dictionary"""
		raw_data_dict = {
			'dispell': {
				'kb_id': 'dispell',
				'profit': 1,
				'price': 2000,
				'school': 1,
				'mana_cost': [5, 5, 5],
				'crystal_cost': [1, 2, 5],
				'data': {}
			},
			'titan_sword': {
				'kb_id': 'titan_sword',
				'profit': 4,
				'price': 50000,
				'school': 5,
				'mana_cost': None,
				'crystal_cost': None,
				'data': {}
			}
		}

		spells = factory.create_batch_from_raw_data(raw_data_dict)

		assert len(spells) == 2
		assert spells[0].kb_id == 'dispell'
		assert spells[0].school == SpellSchool.ORDER
		assert spells[0].loc is not None
		assert spells[0].loc.name == 'Dispel'
		assert spells[1].kb_id == 'titan_sword'
		assert spells[1].school == SpellSchool.WANDERING
		assert spells[1].loc is not None
		assert spells[1].loc.name == 'Titan Sword'

	def test_create_with_complex_data_structure(self, factory):
		"""Test that complex nested data is preserved"""
		raw_data = {
			'kb_id': 'dispell',
			'profit': 1,
			'price': 2000,
			'school': 1,
			'data': {
				'scripted': {
					'no_hint': 1,
					'script_attack': 'spell_dispell_attack',
					'script_calccells': 'calccells_spell_dispell',
					'attack_cursor': 'magicstick',
					'ad_factor': 0,
					'nfeatures': ['magic_immunitet', 'pawn', 'boss']
				},
				'params': {
					'duration': 0,
					'type': 'bonus',
					'exception': [
						'effect_burn',
						'effect_freeze',
						'effect_poison',
						'effect_bleed'
					],
					'target': ['ally', 'all', 'all'],
					'ally_dispell': ['all', 'all', 'penalty'],
					'enemy_dispell': ['none', 'all', 'bonus']
				},
				'raw': {
					'category': 's',
					'image': 'book_spell_dispell.png',
					'button_image': 'book_scroll_dispell.png'
				}
			}
		}

		spell = factory.create_from_raw_data(raw_data)

		assert spell.data['scripted']['nfeatures'] == ['magic_immunitet', 'pawn', 'boss']
		assert spell.data['params']['exception'] == [
			'effect_burn',
			'effect_freeze',
			'effect_poison',
			'effect_bleed'
		]
		assert spell.data['params']['ally_dispell'] == ['all', 'all', 'penalty']
		assert spell.data['raw']['image'] == 'book_spell_dispell.png'

	def test_loc_fetch_does_not_match_similar_spell_names(self, loc_factory, mock_localization_repo):
		"""Test that fetching localizations for 'empathy' doesn't match 'empathy2'"""
		# Add empathy and empathy2 localizations to mock repo
		mock_localization_repo.list_all = lambda tag=None: [
			Localization(id=1, kb_id='spell_empathy_name', text='Empathy', source='spells', tag='spells'),
			Localization(id=2, kb_id='spell_empathy_hint', text='Empathy hint', source='spells', tag='spells'),
			Localization(id=3, kb_id='spell_empathy2_name', text='Empathy 2', source='spells', tag='spells'),
			Localization(id=4, kb_id='spell_empathy2_hint', text='Empathy 2 hint', source='spells', tag='spells'),
		]

		factory = SpellFactory(
			loc_factory=loc_factory,
			localization_repository=mock_localization_repo
		)

		# Create spell for 'empathy' (NOT 'empathy2')
		raw_data = {
			'kb_id': 'empathy',
			'profit': 1,
			'price': 1000,
			'school': 1,
			'data': {}
		}

		spell = factory.create_from_raw_data(raw_data)

		# Should only have localizations for 'empathy', not 'empathy2'
		assert spell.loc is not None
		assert spell.loc.name == 'Empathy'
		assert spell.loc.hint == 'Empathy hint'
		# texts should have exactly 2 entries (empathy_name and empathy_hint)
		assert len(spell.loc.texts) == 2
		assert 'spell_empathy_name' in spell.loc.texts
		assert 'spell_empathy_hint' in spell.loc.texts
		# Should NOT contain empathy2 localizations
		assert 'spell_empathy2_name' not in spell.loc.texts
		assert 'spell_empathy2_hint' not in spell.loc.texts
