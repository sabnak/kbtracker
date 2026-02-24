from abc import ABC, abstractmethod

from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.Localization import Localization


class ILocFactory(ABC):

	@abstractmethod
	def create_from_localizations(self, localizations: list[Localization]) -> LocStrings:
		"""
		Create LocStrings from list of Localization entities

		Maps localization kb_id suffixes to LocStrings fields:
		- *_name -> name (exact match, no duplicates)
		- *_hint -> hint (exact match, no duplicates)
		- *_desc (exact) -> desc (no duplicates)
		- *_desc_\d+ (indexed) -> desc_list (allows multiple)
		- *_text (exact) -> text (no duplicates)
		- *_text_\d+ (indexed) -> text_list (allows multiple)
		- *_header -> header (exact match, no duplicates)
		Non-matching suffixes are dropped silently

		:param localizations:
			List of Localization entities
		:return:
			LocStrings with mapped fields
		:raises Exception:
			If duplicate exact suffix types found (e.g., two _name entries)
		"""
		pass
