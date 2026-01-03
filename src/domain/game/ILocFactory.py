from abc import ABC, abstractmethod

from src.domain.game.entities.LocStrings import LocStrings
from src.domain.game.entities.Localization import Localization


class ILocFactory(ABC):

	@abstractmethod
	def create_from_localizations(self, localizations: list[Localization]) -> LocStrings:
		"""
		Create LocStrings from list of Localization entities

		Maps localization kb_id suffixes to LocStrings fields:
		- *_name -> name
		- *_hint -> hint
		- *_desc -> desc
		- *_header -> header
		All localizations stored in texts dict

		:param localizations:
			List of Localization entities for a spell
		:return:
			LocStrings with mapped fields
		:raises Exception:
			If duplicate suffix types found (e.g., two _name entries)
		"""
		pass
