import pytest

from src.domain.game.entities.Localization import Localization
from src.domain.game.factories.LocFactory import LocFactory


class TestLocFactory:

	@pytest.fixture
	def factory(self):
		"""Create LocFactory"""
		return LocFactory()

	def test_create_with_all_suffix_types(self, factory):
		"""Test creating LocEntity with all localization suffix types"""
		localizations = [
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
			)
		]

		loc_entity = factory.create_from_localizations(localizations)

		assert loc_entity.name == 'Dispel'
		assert loc_entity.hint == 'Removes all effects from target unit'
		assert loc_entity.desc == 'This spell removes all magical effects'
		assert loc_entity.header == 'Order Magic'
		assert isinstance(loc_entity.texts, dict)
		assert len(loc_entity.texts) == 4
		assert loc_entity.texts['spell_dispell_name'] == 'Dispel'
		assert loc_entity.texts['spell_dispell_hint'] == 'Removes all effects from target unit'
		assert loc_entity.texts['spell_dispell_desc'] == 'This spell removes all magical effects'
		assert loc_entity.texts['spell_dispell_header'] == 'Order Magic'

	def test_create_with_partial_fields(self, factory):
		"""Test creating LocEntity with only some localization fields"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_titan_sword_name',
				text='Titan Sword',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_titan_sword_hint',
				text='Summon the legendary Titan Sword',
				source='spells',
				tag='spells'
			)
		]

		loc_entity = factory.create_from_localizations(localizations)

		assert loc_entity.name == 'Titan Sword'
		assert loc_entity.hint == 'Summon the legendary Titan Sword'
		assert loc_entity.desc is None
		assert loc_entity.header is None
		assert isinstance(loc_entity.texts, dict)
		assert len(loc_entity.texts) == 2
		assert loc_entity.texts['spell_titan_sword_name'] == 'Titan Sword'
		assert loc_entity.texts['spell_titan_sword_hint'] == 'Summon the legendary Titan Sword'

	def test_create_with_only_name(self, factory):
		"""Test creating LocEntity with only name field"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_test_name',
				text='Test Spell',
				source='spells',
				tag='spells'
			)
		]

		loc_entity = factory.create_from_localizations(localizations)

		assert loc_entity.name == 'Test Spell'
		assert loc_entity.hint is None
		assert loc_entity.desc is None
		assert loc_entity.header is None
		assert isinstance(loc_entity.texts, dict)
		assert len(loc_entity.texts) == 1

	def test_create_from_empty_list(self, factory):
		"""Test creating LocEntity from empty list"""
		localizations = []

		loc_entity = factory.create_from_localizations(localizations)

		assert loc_entity.name is None
		assert loc_entity.hint is None
		assert loc_entity.desc is None
		assert loc_entity.header is None
		assert loc_entity.texts is None

	def test_exception_on_duplicate_name_suffix(self, factory):
		"""Test that exception is raised when duplicate _name suffix is found"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_name',
				text='Dispel',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_another_dispell_name',
				text='Another Dispel',
				source='spells',
				tag='spells'
			)
		]

		with pytest.raises(Exception) as exc_info:
			factory.create_from_localizations(localizations)

		assert 'Duplicate _name suffix found' in str(exc_info.value)

	def test_exception_on_duplicate_hint_suffix(self, factory):
		"""Test that exception is raised when duplicate _hint suffix is found"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_hint',
				text='First hint',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_another_hint',
				text='Second hint',
				source='spells',
				tag='spells'
			)
		]

		with pytest.raises(Exception) as exc_info:
			factory.create_from_localizations(localizations)

		assert 'Duplicate _hint suffix found' in str(exc_info.value)

	def test_exception_on_duplicate_desc_suffix(self, factory):
		"""Test that exception is raised when duplicate _desc suffix is found"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_desc',
				text='First description',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_another_desc',
				text='Second description',
				source='spells',
				tag='spells'
			)
		]

		with pytest.raises(Exception) as exc_info:
			factory.create_from_localizations(localizations)

		assert 'Duplicate _desc suffix found' in str(exc_info.value)

	def test_exception_on_duplicate_header_suffix(self, factory):
		"""Test that exception is raised when duplicate _header suffix is found"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_header',
				text='First header',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_another_header',
				text='Second header',
				source='spells',
				tag='spells'
			)
		]

		with pytest.raises(Exception) as exc_info:
			factory.create_from_localizations(localizations)

		assert 'Duplicate _header suffix found' in str(exc_info.value)

	def test_non_matching_suffixes_preserved_in_texts(self, factory):
		"""Test that localizations without standard suffixes are preserved in texts"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_dispell_name',
				text='Dispel',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_dispell_custom_field',
				text='Custom field value',
				source='spells',
				tag='spells'
			),
			Localization(
				id=3,
				kb_id='spell_dispell_another_custom',
				text='Another custom value',
				source='spells',
				tag='spells'
			)
		]

		loc_entity = factory.create_from_localizations(localizations)

		assert loc_entity.name == 'Dispel'
		assert loc_entity.hint is None
		assert loc_entity.desc is None
		assert loc_entity.header is None
		assert len(loc_entity.texts) == 3
		assert loc_entity.texts['spell_dispell_custom_field'] == 'Custom field value'
		assert loc_entity.texts['spell_dispell_another_custom'] == 'Another custom value'

	def test_mixed_prefixes_all_fields_mapped(self, factory):
		"""Test that different prefixes are handled correctly"""
		localizations = [
			Localization(
				id=1,
				kb_id='spell_fire_name',
				text='Fire Spell',
				source='spells',
				tag='spells'
			),
			Localization(
				id=2,
				kb_id='spell_ice_hint',
				text='Ice hint',
				source='spells',
				tag='spells'
			),
			Localization(
				id=3,
				kb_id='spell_water_desc',
				text='Water description',
				source='spells',
				tag='spells'
			),
			Localization(
				id=4,
				kb_id='spell_earth_header',
				text='Earth header',
				source='spells',
				tag='spells'
			)
		]

		loc_entity = factory.create_from_localizations(localizations)

		# All should map to their respective fields despite different prefixes
		assert loc_entity.name == 'Fire Spell'
		assert loc_entity.hint == 'Ice hint'
		assert loc_entity.desc == 'Water description'
		assert loc_entity.header == 'Earth header'
		assert len(loc_entity.texts) == 4
