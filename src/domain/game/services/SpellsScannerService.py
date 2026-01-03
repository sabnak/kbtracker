from dependency_injector.wiring import Provide, inject

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.entities.Spell import Spell
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.ISpellFactory import ISpellFactory
from src.domain.game.ISpellRepository import ISpellRepository
from src.domain.game.ISpellsScannerService import ISpellsScannerService
from src.utils.parsers.game_data.IKFSSpellsParser import IKFSSpellsParser


class SpellsScannerService(ISpellsScannerService):

	@inject
	def __init__(
		self,
		spell_repository: ISpellRepository = Provide[Container.spell_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: IKFSSpellsParser = Provide[Container.kfs_spells_parser],
		spell_factory: ISpellFactory = Provide[Container.spell_factory],
		config: Config = Provide[Container.config]
	):
		"""
		Initialize spells scanner service

		:param spell_repository:
			Spell repository
		:param game_repository:
			Game repository
		:param parser:
			KFS spells parser
		:param spell_factory:
			Spell factory
		:param config:
			Application configuration
		"""
		self._spell_repository = spell_repository
		self._game_repository = game_repository
		self._parser = parser
		self._spell_factory = spell_factory
		self._config = config

	def scan(self, game_id: int, game_name: str) -> list[Spell]:
		"""
		Scan and import spells from game files

		:param game_id:
			Game ID
		:param game_name:
			Game name for file paths
		:return:
			List of created Spell entities
		"""
		raw_data_dict = self._parser.parse(game_name)
		spells = self._spell_factory.create_batch_from_raw_data(raw_data_dict)
		created_spells = self._spell_repository.create_batch(spells)
		return created_spells
