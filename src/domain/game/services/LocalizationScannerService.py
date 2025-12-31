import os

from dependency_injector.wiring import Provide, inject

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.ILocalizationScannerService import ILocalizationScannerService
from src.domain.game.entities.Localization import Localization
from src.domain.game.utils.KFSLocalizationParser import KFSLocalizationParser


class LocalizationScannerService(ILocalizationScannerService):

	def __init__(
		self,
		repository: ILocalizationRepository = Provide[Container.localization_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: KFSLocalizationParser = Provide[Container.kfs_localization_parser],
		config: Config = Provide[Container.config]
	):
		self._parser = parser
		self._repository = repository
		self._game_repository = game_repository
		self._config = config

	def scan(self, game_id: int, lang: str = 'rus') -> list[Localization]:
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		sessions_path = os.path.join(self._config.game_data_path, game.path, "sessions")
		all_localizations = []

		for localization_config in self._config.localization_config:
			localizations = self._parser.parse(
				sessions_path=sessions_path,
				file_name=localization_config.file,
				kb_id_pattern=localization_config.pattern,
				lang=lang,
				tag=localization_config.tag
			)
			all_localizations.extend(localizations)

		return self._repository.create_batch(all_localizations)
