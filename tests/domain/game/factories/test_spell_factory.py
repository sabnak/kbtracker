import pytest

from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.factories.SpellFactory import SpellFactory


class TestSpellFactory:

	@pytest.fixture
	def factory(self):
		"""Create factory"""
		return SpellFactory()

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
		assert spell.loc is None

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
		assert spell.loc is None

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

	def test_loc_is_none_for_all_spells(self, factory):
		"""Test that loc is always None (enriched by repository)"""
		raw_data = {
			'kb_id': 'test_spell',
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
		assert spells[0].loc is None
		assert spells[1].kb_id == 'titan_sword'
		assert spells[1].school == SpellSchool.WANDERING
		assert spells[1].loc is None

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
