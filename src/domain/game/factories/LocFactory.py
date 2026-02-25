import re

from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.Localization import Localization
from src.domain.game.interfaces.ILocFactory import ILocFactory


class LocFactory(ILocFactory):

	_EXACT_NAME = re.compile(r'_name$')
	_EXACT_HINT = re.compile(r'_hint$')
	_EXACT_DESC = re.compile(r'_desc$')
	_EXACT_TEXT = re.compile(r'_text$')
	_EXACT_HEADER = re.compile(r'_header$')
	_INDEXED_DESC = re.compile(r'_desc_(\d+)$')
	_INDEXED_TEXT = re.compile(r'_text_(\d+)$')

	def create_from_localizations(self, localizations: list[Localization]) -> LocStrings:
		name = None
		hint = None
		desc = None
		desc_list = []
		text = None
		text_list = []
		header = None

		name_count = 0
		hint_count = 0
		desc_count = 0
		text_count = 0
		header_count = 0

		for loc in localizations:
			kb_id = loc.kb_id

			if self._EXACT_NAME.search(kb_id):
				name_count += 1
				if name_count > 1:
					raise Exception(f"Duplicate _name suffix found in localizations: {kb_id}")
				name = loc.text

			elif self._EXACT_HINT.search(kb_id):
				hint_count += 1
				if hint_count > 1:
					raise Exception(f"Duplicate _hint suffix found in localizations: {kb_id}")
				hint = loc.text

			elif self._EXACT_DESC.search(kb_id):
				desc_count += 1
				if desc_count > 1:
					raise Exception(f"Duplicate _desc suffix found in localizations: {kb_id}")
				desc = loc.text

			elif self._INDEXED_DESC.search(kb_id):
				desc_list.append(loc.text)

			elif self._EXACT_TEXT.search(kb_id):
				text_count += 1
				if text_count > 1:
					raise Exception(f"Duplicate _text suffix found in localizations: {kb_id}")
				text = loc.text

			elif self._INDEXED_TEXT.search(kb_id):
				text_list.append(loc.text)

			elif self._EXACT_HEADER.search(kb_id):
				header_count += 1
				if header_count > 1:
					raise Exception(f"Duplicate _header suffix found in localizations: {kb_id}")
				header = loc.text

		return LocStrings(
			name=name,
			hint=hint,
			desc=desc,
			desc_list=desc_list if desc_list else None,
			text=text,
			text_list=text_list if text_list else None,
			header=header
		)
