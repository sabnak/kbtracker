from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.game.entities.Localization import Localization
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.game.interfaces.ILocalizationScannerService import ILocalizationScannerService
from src.utils.parsers.game_data.IKFSLocalizationParser import IKFSLocalizationParser


class LocalizationScannerService(ILocalizationScannerService):

	def __init__(
		self,
		repository: ILocalizationRepository = Provide[Container.localization_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: IKFSLocalizationParser = Provide[Container.kfs_localization_parser],
		config: Config = Provide[Container.config]
	):
		self._parser = parser
		self._repository = repository
		self._game_repository = game_repository
		self._config = config

	def scan(self, game_id: int, game_name: str, lang: str = 'rus') -> list[Localization]:
		all_localizations = dict()

		for localization_config in self._config.localization_config:
			try:
				localizations = self._parser.parse(
					game_name=game_name,
					file_name=localization_config.file,
					kb_id_pattern=localization_config.pattern,
					lang=lang,
					tag=localization_config.tag
				)
			except FileNotFoundError:
				continue
			all_localizations.update(localizations)

		if not all_localizations:
			raise FileNotFoundError(f"Can't find any localizations files for {game_name}")

		return self._repository.create_batch(list(all_localizations.values()))
