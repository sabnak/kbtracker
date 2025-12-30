from abc import ABC, abstractmethod

from src.domain.game.entities.Localization import Localization


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
	def get_by_kb_id(self, kb_id: str) -> Localization | None:
		"""
		Get localization by game identifier

		:param kb_id:
			Game identifier
		:return:
			Localization or None if not found
		"""
		pass

	@abstractmethod
	def search_by_text(self, query: str) -> list[Localization]:
		"""
		Search localization text (case-insensitive)

		:param query:
			Search query
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
