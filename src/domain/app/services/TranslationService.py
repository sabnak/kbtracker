import os

from babel.support import Translations, NullTranslations
from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.domain.app.entities.AppLanguage import AppLanguage
from src.domain.app.interfaces.ISettingsService import ISettingsService
from src.domain.app.interfaces.ITranslationService import ITranslationService


class TranslationService(ITranslationService):

	@inject
	def __init__(
		self,
		settings_service: ISettingsService = Provide[Container.settings_service]
	):
		self._settings_service = settings_service
		self._translations_cache: dict[str, Translations] = {}

	def gettext(self, message: str) -> str:
		"""
		Translate message key to current language

		:param message:
			Translation key (e.g., "ui.items", "game.spell_name")
		:return:
			Translated string or key if translation not found
		"""
		locale = self.get_current_locale()
		translations = self._get_translations(locale)
		return translations.gettext(message)

	def get_current_locale(self) -> str:
		"""
		Get current locale code

		:return:
			Locale code ("ru" or "en")
		"""
		language = self._settings_service.get_settings().language
		return "ru" if language == AppLanguage.RUSSIAN else "en"

	def _get_translations(self, locale: str) -> Translations:
		"""
		Load translation catalog for given locale

		:param locale:
			Locale code ("ru" or "en")
		:return:
			Translations object
		"""
		if locale in self._translations_cache:
			return self._translations_cache[locale]

		translations_dir = os.path.join(
			os.path.dirname(__file__),
			"..", "..", "..", "i18n", "translations"
		)
		translations_dir = os.path.abspath(translations_dir)

		try:
			translations = Translations.load(
				dirname=translations_dir,
				locales=[locale],
				domain="messages"
			)
			self._translations_cache[locale] = translations
			return translations
		except FileNotFoundError:
			if locale != "en":
				return self._get_translations("en")

			return NullTranslations()
