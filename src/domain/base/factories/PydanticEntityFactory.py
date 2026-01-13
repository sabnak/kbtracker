import typing

import pydantic

from src.domain.base.repositories.mappers.base import Base

T = typing.TypeVar("T", bound=pydantic.BaseModel)


class PydanticEntityFactory:

	@staticmethod
	def create_entity(
		t: typing.Type[T],
		mapper: Base,
		**additional_data
	) -> T:
		entity = t.model_validate(mapper, extra='ignore')
		if additional_data:
			return entity.model_copy(update=additional_data)
		return entity
