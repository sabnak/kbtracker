import abc


class ITranslationService(abc.ABC):

	@abc.abstractmethod
	def gettext(self, message: str) -> str:
		"""
		Translate message key to current language

		:param message:
			Translation key (e.g., "ui.items", "game.spell_name")
		:return:
			Translated string or key if translation not found
		"""
		...

	@abc.abstractmethod
	def get_current_locale(self) -> str:
		"""
		Get current locale code

		:return:
			Locale code ("ru" or "en")
		"""
		...
