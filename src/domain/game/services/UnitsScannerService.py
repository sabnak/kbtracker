from dependency_injector.wiring import Provide, inject

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IUnitRepository import IUnitRepository
from src.domain.game.IUnitsScannerService import IUnitsScannerService
from src.domain.game.entities.Unit import Unit
from src.utils.parsers.game_data.IKFSUnitParser import IKFSUnitParser


class UnitsScannerService(IUnitsScannerService):

	@inject
	def __init__(
		self,
		unit_repository: IUnitRepository = Provide[Container.unit_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: IKFSUnitParser = Provide[Container.kfs_unit_parser],
		config: Config = Provide[Container.config]
	):
		"""
		Initialize units scanner service

		:param unit_repository:
			Unit repository
		:param game_repository:
			Game repository
		:param parser:
			KFS unit parser
		:param config:
			Application configuration
		"""
		self._unit_repository = unit_repository
		self._game_repository = game_repository
		self._parser = parser
		self._config = config

	def scan(self, game_id: int, game_name: str) -> list[Unit]:
		"""
		Scan and import units from game files

		:param game_id:
			Game ID
		:param game_name:
			Game name for file paths
		:return:
			List of created Unit entities
		"""
		units = self._parser.parse(game_name)
		created_units = self._unit_repository.create_batch(units)
		return created_units
