from src.domain.game.entities.LocEntity import LocEntity
from src.domain.game.entities.Localization import Localization
from src.domain.game.ILocFactory import ILocFactory


class LocFactory(ILocFactory):

	def create_from_localizations(self, localizations: list[Localization]) -> LocEntity:
		"""
		Create LocEntity from list of Localization entities

		Maps localization kb_id suffixes to LocEntity fields:
		- *_name -> name
		- *_hint -> hint
		- *_desc -> desc
		- *_header -> header
		All localizations stored in texts dict

		:param localizations:
			List of Localization entities for a spell
		:return:
			LocEntity with mapped fields
		:raises Exception:
			If duplicate suffix types found (e.g., two _name entries)
		"""
		name = None
		hint = None
		desc = None
		header = None
		texts = {}

		name_count = 0
		hint_count = 0
		desc_count = 0
		header_count = 0

		for loc in localizations:
			kb_id = loc.kb_id
			texts[kb_id] = loc.text

			if kb_id.endswith('_name'):
				name_count += 1
				if name_count > 1:
					raise Exception(f"Duplicate _name suffix found in localizations: {kb_id}")
				name = loc.text
			elif kb_id.endswith('_hint'):
				hint_count += 1
				if hint_count > 1:
					raise Exception(f"Duplicate _hint suffix found in localizations: {kb_id}")
				hint = loc.text
			elif kb_id.endswith('_desc'):
				desc_count += 1
				if desc_count > 1:
					raise Exception(f"Duplicate _desc suffix found in localizations: {kb_id}")
				desc = loc.text
			elif kb_id.endswith('_header'):
				header_count += 1
				if header_count > 1:
					raise Exception(f"Duplicate _header suffix found in localizations: {kb_id}")
				header = loc.text

		return LocEntity(
			name=name,
			hint=hint,
			desc=desc,
			header=header,
			texts=texts if texts else None
		)
