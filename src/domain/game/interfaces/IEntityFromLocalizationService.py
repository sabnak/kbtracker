import typing
from abc import ABC, abstractmethod

from src.domain.game.entities.GameEntity import GameEntity

TEntity = typing.TypeVar("TEntity", bound=GameEntity)


class IEntityFromLocalizationService(ABC, typing.Generic[TEntity]):

	@abstractmethod
	def scan(self, game_id: int) -> list[TEntity]:
		pass
