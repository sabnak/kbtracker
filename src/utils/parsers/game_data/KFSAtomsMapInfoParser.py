import re

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.AtomMap import AtomMap
from src.domain.game.entities.Localization import Localization
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.utils.parsers.game_data.IKFSAtomsMapInfoParser import IKFSAtomsMapInfoParser


class KFSAtomsMapInfoParser(IKFSAtomsMapInfoParser):

	def __init__(
		self,
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		self._localization_repository = localization_repository

	def parse(self, game_name: str) -> list[AtomMap]:
		localizations = self._localization_repository.list_all(tag='atoms_info')

		atom_kb_ids = self._extract_unique_kb_ids(localizations)

		return [AtomMap(id=0, kb_id=kb_id) for kb_id in atom_kb_ids]

	def _extract_unique_kb_ids(self, localizations: list[Localization]) -> set[str]:
		pattern = re.compile(r'^itext_(.+_\d+)_\w+$')

		kb_ids = set()
		for loc in localizations:
			match = pattern.match(loc.kb_id)
			if match:
				kb_ids.add(match.group(1))

		return kb_ids
