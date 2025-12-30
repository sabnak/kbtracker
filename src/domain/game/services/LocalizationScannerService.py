from dependency_injector.wiring import Provide, inject
import re

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.ILocalizationScannerService import ILocalizationScannerService
from src.domain.game.entities.Localization import Localization
from src.domain.game.utils.KFSLocalizationParser import KFSLocalizationParser


class LocalizationScannerService(ILocalizationScannerService):

	@inject
	def __init__(
		self,
		repository: ILocalizationRepository = Provide[Container.localization_repository],
		config: Config = Provide[Container.config]
	):
		"""
		Initialize localization scanner service

		:param repository:
			Localization repository for persistence
		:param config:
			Application configuration
		"""
		self._parser = KFSLocalizationParser()
		self._repository = repository
		self._config = config

	def scan(
		self,
		sessions_path: str,
		kb_id_pattern: re.Pattern = None,
		lang: str = 'rus'
	) -> list[Localization]:
		"""
		Scan and import localization entries from game files

		:param sessions_path:
			Absolute path to sessions directory
		:param kb_id_pattern:
			Optional regex pattern
		:param lang:
			Language code
		:return:
			Created localizations with database IDs
		"""
		all_localizations = []

		for file_name in self._config.localization_files:
			localizations = self._parser.parse(
				sessions_path=sessions_path,
				file_name=file_name,
				kb_id_pattern=kb_id_pattern,
				lang=lang
			)
			all_localizations.extend(localizations)

		return self._repository.create_batch(all_localizations)
