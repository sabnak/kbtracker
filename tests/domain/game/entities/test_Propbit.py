import pytest
from src.domain.game.entities.Propbit import Propbit


class TestPropbit:

	def test_enum_has_all_expected_members(self):
		"""
		Test that Propbit enum contains all 19 expected values
		"""
		expected_members = {
			'ARMOR', 'ARTEFACT', 'BELT', 'BOOTS', 'CONTAINER',
			'DIALOG', 'GLOVES', 'HELMET', 'HIDDEN', 'MORAL',
			'MULTIUSE', 'PANTS', 'QUEST', 'RARE', 'REGALIA',
			'SHIELD', 'USABLE', 'WEAPON', 'WIFE'
		}
		actual_members = {member.name for member in Propbit}
		assert actual_members == expected_members

	def test_enum_values_are_lowercase(self):
		"""
		Test that all enum values are lowercase strings
		"""
		for member in Propbit:
			assert member.value.islower()
			assert member.value == member.name.lower()

	def test_can_instantiate_from_string(self):
		"""
		Test that Propbit can be created from string value
		"""
		armor = Propbit("armor")
		assert armor == Propbit.ARMOR
		assert armor.value == "armor"

	def test_invalid_string_raises_value_error(self):
		"""
		Test that invalid propbit string raises ValueError
		"""
		with pytest.raises(ValueError):
			Propbit("invalid_propbit")

	def test_enum_string_comparison(self):
		"""
		Test that Propbit enum can be compared with strings (str mixin)
		"""
		assert Propbit.ARMOR == "armor"
		assert "weapon" == Propbit.WEAPON
