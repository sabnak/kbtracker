import pytest
import re

from src.domain.exceptions import (
	InvalidRegexPatternException,
	NoLocalizationMatchesException
)


class TestKFSLocalizationParser:

	@pytest.fixture(autouse=True)
	def setup(self, extracted_game_files):
		"""
		Auto-use fixture that ensures archives are extracted before tests

		:param extracted_game_files:
			Extraction root path
		"""
		pass

	def test_parse_with_default_pattern_returns_localizations(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test parsing with default kb_id pattern
		"""
		localizations = kfs_localization_parser.parse(test_game_name, 'items')

		assert len(localizations) > 0
		assert all(loc.id == 0 for loc in localizations)
		assert all(loc.source == 'items' for loc in localizations)
		assert all(loc.kb_id for loc in localizations)
		assert all(loc.text for loc in localizations)

	def test_parse_with_russian_language(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test archive path for Russian language
		"""
		localizations = kfs_localization_parser.parse(test_game_name, 'items', lang='rus')

		assert len(localizations) > 0

	@pytest.mark.parametrize("kb_id,text", [
		("magical_recipe_price_no", "Отсутствуют"),
		("valk1_bonus_info_1", "Прими же мою ярость, сын Тормунда!<br><color=138,138,132>Вы получили 5 Ярости!"),
	])
	def test_parse_extracts_correct_kb_id_and_text(
		self,
		kfs_localization_parser,
		test_game_name,
		kb_id,
		text
	):
		"""
		Test that specific kb_id and text pairs are extracted correctly
		"""
		localizations = kfs_localization_parser.parse(test_game_name, 'items')
		localization_dict = {loc.kb_id: loc.text for loc in localizations}

		assert kb_id in localization_dict
		assert localization_dict[kb_id] == text

	def test_parse_with_custom_pattern(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test parsing with custom kb_id pattern
		"""
		custom_pattern = re.compile(r'^(?P<kb_id>valk\w+)', re.I)

		localizations = kfs_localization_parser.parse(
			test_game_name,
			'items',
			kb_id_pattern=custom_pattern
		)

		assert len(localizations) > 0
		assert all(loc.kb_id.startswith('valk') for loc in localizations)

	def test_parse_with_pattern_missing_kb_id_group_raises_exception(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test that pattern without kb_id group raises InvalidRegexPatternException
		"""
		invalid_pattern = re.compile(r'^([-\w]+)')

		with pytest.raises(InvalidRegexPatternException) as exc_info:
			kfs_localization_parser.parse(test_game_name, 'items', kb_id_pattern=invalid_pattern)

		assert exc_info.value.missing_group == 'kb_id'
		assert exc_info.value.pattern == r'^([-\w]+)'

	def test_parse_with_no_matches_raises_exception(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test that no matches raises NoLocalizationMatchesException
		"""
		no_match_pattern = re.compile(r'^(?P<kb_id>XXXNONEXISTENT)', re.I)

		with pytest.raises(NoLocalizationMatchesException) as exc_info:
			kfs_localization_parser.parse(test_game_name, 'items', kb_id_pattern=no_match_pattern)

		assert exc_info.value.file_name == 'items'
		assert exc_info.value.lang == 'rus'

	def test_parse_multiple_entries(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test parsing file with multiple localization entries
		"""
		localizations = kfs_localization_parser.parse(test_game_name, 'items')

		assert len(localizations) > 10

	def test_parse_preserves_source_filename(
		self,
		kfs_localization_parser,
		test_game_name
	):
		"""
		Test that source field is set correctly
		"""
		localizations = kfs_localization_parser.parse(test_game_name, 'items')

		assert all(loc.source == 'items' for loc in localizations)
