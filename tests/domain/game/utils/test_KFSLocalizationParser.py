from pathlib import Path
import pytest
import re

from src.domain.exceptions import (
	InvalidRegexPatternException,
	NoLocalizationMatchesException
)
from src.domain.game.parsers.game_data.KFSLocalizationParser import KFSLocalizationParser


class TestKFSLocalizationParser:

	@pytest.fixture
	def sessions_path(self) -> str:
		"""
		Fixture for test game files sessions path

		:return:
			Absolute path to test sessions directory
		"""
		return str(Path(__file__).parent.parent.parent.parent.parent / "tests" / "game_files" / "sessions")

	@pytest.fixture
	def parser(self) -> KFSLocalizationParser:
		"""
		Fixture for parser instance

		:return:
			KFSLocalizationParser instance
		"""
		return KFSLocalizationParser()

	def test_parse_with_default_pattern_returns_localizations(
		self,
		parser,
		sessions_path
	):
		"""
		Test parsing with default kb_id pattern
		"""
		localizations = parser.parse(1, sessions_path, 'items')

		assert len(localizations) > 0
		assert all(loc.id == 0 for loc in localizations)
		assert all(loc.source == 'items' for loc in localizations)
		assert all(loc.kb_id for loc in localizations)
		assert all(loc.text for loc in localizations)

	def test_parse_with_russian_language(self, parser, sessions_path):
		"""
		Test archive path for Russian language
		"""
		localizations = parser.parse(1, sessions_path, 'items', lang='rus')

		assert len(localizations) > 0

	@pytest.mark.parametrize("kb_id,text", [
		("magical_recipe_price_no", "Отсутствуют"),
		("valk1_bonus_info_1", "Прими же мою ярость, сын Тормунда!<br><color=138,138,132>Вы получили 5 Ярости!"),
	])
	def test_parse_extracts_correct_kb_id_and_text(
		self,
		parser,
		sessions_path,
		kb_id,
		text
	):
		"""
		Test that specific kb_id and text pairs are extracted correctly
		"""
		localizations = parser.parse(1, sessions_path, 'items')
		localization_dict = {loc.kb_id: loc.text for loc in localizations}

		assert kb_id in localization_dict
		assert localization_dict[kb_id] == text

	def test_parse_with_custom_pattern(self, parser, sessions_path):
		"""
		Test parsing with custom kb_id pattern
		"""
		custom_pattern = re.compile(r'^(?P<kb_id>valk\w+)', re.I)

		localizations = parser.parse(
			1,
			sessions_path,
			'items',
			kb_id_pattern=custom_pattern
		)

		assert len(localizations) > 0
		assert all(loc.kb_id.startswith('valk') for loc in localizations)

	def test_parse_with_pattern_missing_kb_id_group_raises_exception(
		self,
		parser,
		sessions_path
	):
		"""
		Test that pattern without kb_id group raises InvalidRegexPatternException
		"""
		invalid_pattern = re.compile(r'^([-\w]+)')

		with pytest.raises(InvalidRegexPatternException) as exc_info:
			parser.parse(1, sessions_path, 'items', kb_id_pattern=invalid_pattern)

		assert exc_info.value.missing_group == 'kb_id'
		assert exc_info.value.pattern == r'^([-\w]+)'

	def test_parse_with_no_matches_raises_exception(self, parser, sessions_path):
		"""
		Test that no matches raises NoLocalizationMatchesException
		"""
		no_match_pattern = re.compile(r'^(?P<kb_id>XXXNONEXISTENT)', re.I)

		with pytest.raises(NoLocalizationMatchesException) as exc_info:
			parser.parse(1, sessions_path, 'items', kb_id_pattern=no_match_pattern)

		assert exc_info.value.file_name == 'items'
		assert exc_info.value.lang == 'rus'

	def test_parse_multiple_entries(self, parser, sessions_path):
		"""
		Test parsing file with multiple localization entries
		"""
		localizations = parser.parse(1, sessions_path, 'items')

		assert len(localizations) > 10

	def test_parse_preserves_source_filename(self, parser, sessions_path):
		"""
		Test that source field is set correctly
		"""
		localizations = parser.parse(1, sessions_path, 'items')

		assert all(loc.source == 'items' for loc in localizations)
