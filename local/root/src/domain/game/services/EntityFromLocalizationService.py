import re
import typing

from dependency_injector.wiring import Provide

from src.core.Container import Container
from src.domain.game.entities.Localization import Localization
from src.domain.game.interfaces.IEntityFromLocalizationService import IEntityFromLocalizationService, TEntity
from src.domain.game.interfaces.IEntityRepository import IEntityRepository
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository


class EntityFromLocalizationService(IEntityFromLocalizationService):

	def __init__(
		self,
		entity_type: typing.Type[TEntity],
		kb_pattern: str,
		localization_tag: str,
		entity_repository: IEntityRepository[TEntity],
		localization_repository: ILocalizationRepository = Provide[Container.localization_repository]
	):
		self._repository = entity_repository
		self._localization_repository = localization_repository
		self._entity_type = entity_type
		self._kb_pattern = kb_pattern
		self._localization_tag = localization_tag

	def scan(self, game_id: int) -> list[TEntity]:
		entities = self._parse()
		if not entities:
			return []
		return self._repository.create_batch(entities)

	def _parse(self) -> list[TEntity]:
		localizations = self._localization_repository.list_all(tag=self._localization_tag)
		kb_ids = self._extract_unique_kb_ids(localizations)
		return [self._entity_type(id=0, kb_id=kb_id) for kb_id in kb_ids]

	def _extract_unique_kb_ids(self, localizations: list[Localization]) -> set[str]:
		pattern = re.compile(self._kb_pattern)

		kb_ids = set()
		for loc in localizations:
			match = pattern.match(loc.kb_id)
			if match:
				kb_ids.add(match.group(1))

		return kb_ids
