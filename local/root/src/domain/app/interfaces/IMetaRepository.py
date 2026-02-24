import abc
import typing

import pydantic

from src.domain.app.entities.MetaName import MetaName

T = typing.TypeVar('T', bound=pydantic.BaseModel)


class IMetaRepository(abc.ABC):

	@abc.abstractmethod
	def get(self, name: MetaName) -> T:
		...

	@abc.abstractmethod
	def save(self, name: MetaName, entity: T) -> None:
		...
