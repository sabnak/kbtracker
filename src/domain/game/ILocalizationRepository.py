from abc import ABC, abstractmethod

from src.domain.game.entities.Localization import Localization
from src.domain.game.entities.LocalizationType import LocalizationType


class ILocalizationRepository(ABC):

	@abstractmethod
	def create(self, localization: Localization) -> Localization:
		"""
		Create new localization entry

		:param localization:
			Localization to create
		:return:
			Created localization with ID
		"""
		pass

	@abstractmethod
	def create_batch(self, localizations: list[Localization]) -> list[Localization]:
		"""
		Create multiple localization entries

		:param localizations:
			Localizations to create
		:return:
			Created localizations with IDs
		"""
		pass

	@abstractmethod
	def get_by_id(self, localization_id: int) -> Localization | None:
		"""
		Get localization by database ID

		:param localization_id:
			Localization ID
		:return:
			Localization or None if not found
		"""
		pass

	@abstractmethod
	def get_by_kb_id_and_type(
		self,
		kb_id: str,
		type: LocalizationType
	) -> Localization | None:
		"""
		Get localization by game identifier and type (composite unique key)

		:param kb_id:
			Game identifier
		:param type:
			Localization type
		:return:
			Localization or None if not found
		"""
		pass

	@abstractmethod
	def list_by_type(self, type: LocalizationType) -> list[Localization]:
		"""
		Get all localizations of a specific type

		:param type:
			Localization type
		:return:
			List of localizations of the specified type
		"""
		pass

	@abstractmethod
	def list_by_kb_id(self, kb_id: str) -> list[Localization]:
		"""
		Get all localizations for a specific kb_id (all types)

		:param kb_id:
			Game identifier
		:return:
			List of localizations with the specified kb_id
		"""
		pass

	@abstractmethod
	def search_by_text(
		self,
		query: str,
		type: LocalizationType | None = None
	) -> list[Localization]:
		"""
		Search localization text, optionally filtered by type

		:param query:
			Search query (case-insensitive)
		:param type:
			Optional localization type filter
		:return:
			List of matching localizations
		"""
		pass

	@abstractmethod
	def list_all(self) -> list[Localization]:
		"""
		Get all localization entries

		:return:
			List of all localizations
		"""
		pass
