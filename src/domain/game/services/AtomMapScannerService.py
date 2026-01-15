from dependency_injector.wiring import Provide, inject

from src.core.Container import Container
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.interfaces.IAtomMapRepository import IAtomMapRepository
from src.domain.game.interfaces.IAtomMapScannerService import IAtomMapScannerService
from src.utils.parsers.game_data.IKFSAtomsMapInfoParser import IKFSAtomsMapInfoParser


class AtomMapScannerService(IAtomMapScannerService):

	def __init__(
		self,
		atom_map_repository: IAtomMapRepository = Provide[Container.atom_map_repository],
		parser: IKFSAtomsMapInfoParser = Provide[Container.kfs_atoms_map_info_parser]
	):
		self._atom_map_repository = atom_map_repository
		self._parser = parser

	def scan(self, game_id: int, game_name: str, language: str) -> list[AtomMap]:
		atom_maps = self._parser.parse(game_name, language)

		if not atom_maps:
			return []

		return self._atom_map_repository.create_batch(atom_maps)
