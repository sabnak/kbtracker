import re

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.exceptions import (
	InvalidKbIdException,
	InvalidRegexPatternException,
	NoLocalizationMatchesException
)
from src.domain.game.entities.Localization import Localization
from src.utils.parsers.game_data.IKFSReader import IKFSReader
from src.utils.parsers.game_data.IKFSLocalizationParser import IKFSLocalizationParser


class KFSLocalizationParser(IKFSLocalizationParser):

	def __init__(self, reader: IKFSReader = Provide[Container.kfs_reader]):
		"""
		Initialize KFS localization parser

		Parser is stateless utility class for extracting localization strings
		from King's Bounty game files
		"""
		self._reader = reader

	def parse(
		self,
		game_name: str,
		file_name: str,
		kb_id_pattern: re.Pattern = None,
		lang: str = 'rus',
		tag: str | None = None
	) -> list[Localization]:
		"""
		Parse localization file and return Localization entities

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:param file_name:
			Base name of localization file (e.g., 'items' for rus_items.lng)
		:param kb_id_pattern:
			Optional regex pattern to match kb_id (must contain 'kb_id' named group)
			Default: ^(?P<kb_id>[-\\w]+)
		:param lang:
			Language code (default: 'rus')
		:param tag:
			Optional tag to categorize localization entries
		:return:
			List of Localization entities with id=0 and source=file_name
		:raises InvalidRegexPatternException:
			When kb_id_pattern missing required 'kb_id' named group
		:raises NoLocalizationMatchesException:
			When no matches found in file
		:raises InvalidKbIdException:
			When extracted kb_id doesn't match pattern ^[-\\w]+$
		"""
		if kb_id_pattern is None:
			kb_id_pattern = re.compile(r'^(?P<kb_id>[-\w]+)', re.I | re.MULTILINE)
		else:
			self._validate_pattern_has_kb_id_group(kb_id_pattern)

		filename = f"{lang}_{file_name}.lng"
		content = self._reader.read_loc_files(game_name, [filename])[0]

		final_pattern = self._build_final_pattern(kb_id_pattern)
		localizations = self._parse_content(content, final_pattern, file_name, lang, tag)

		return localizations

	@staticmethod
	def _validate_pattern_has_kb_id_group(pattern: re.Pattern) -> None:
		"""
		Validate that pattern contains required 'kb_id' named group

		:param pattern:
			Regex pattern to validate
		:raises InvalidRegexPatternException:
			When pattern missing 'kb_id' named group
		"""
		if 'kb_id' not in pattern.groupindex:
			raise InvalidRegexPatternException(
				pattern=pattern.pattern,
				missing_group='kb_id'
			)

	@staticmethod
	def _build_final_pattern(kb_id_pattern: re.Pattern) -> re.Pattern:
		"""
		Extend kb_id pattern with text capture group

		:param kb_id_pattern:
			Base pattern for matching kb_id
		:return:
			Extended pattern with text capture
		"""
		base_pattern = kb_id_pattern.pattern
		extended_pattern = base_pattern + r'=(?P<text>[^\n\r]+)'
		return re.compile(extended_pattern, re.I | re.MULTILINE)

	def _parse_content(
		self,
		content: str,
		pattern: re.Pattern,
		file_name: str,
		lang: str,
		tag: str | None = None
	) -> list[Localization]:
		"""
		Parse file content and create Localization entities

		:param content:
			Raw file content
		:param pattern:
			Regex pattern with kb_id and text groups
		:param file_name:
			Source file name for Localization.source field
		:param lang:
			Language code for error messages
		:param tag:
			Optional tag to categorize localization entries
		:return:
			List of Localization entities
		:raises NoLocalizationMatchesException:
			When no matches found
		:raises InvalidKbIdException:
			When kb_id doesn't match strict format
		"""
		matches = list(pattern.finditer(content))

		if not matches:
			raise NoLocalizationMatchesException(
				file_name=file_name,
				pattern=pattern.pattern,
				lang=lang
			)

		localizations = []
		for match in matches:
			kb_id = match.group('kb_id')
			text = match.group('text')

			self._validate_kb_id(kb_id, file_name)

			localization = Localization(
				id=0,
				kb_id=kb_id,
				text=text,
				source=file_name,
				tag=tag
			)
			localizations.append(localization)

		return localizations

	@staticmethod
	def _validate_kb_id(kb_id: str, source: str) -> None:
		"""
		Validate kb_id against strict format pattern

		:param kb_id:
			KB ID to validate
		:param source:
			Source file name for error messages
		:raises InvalidKbIdException:
			When kb_id doesn't match ^[-\\w]+$
		"""
		strict_pattern = re.compile(r'^[-\w]+$')
		if not strict_pattern.match(kb_id):
			raise InvalidKbIdException(kb_id=kb_id, source=source)
