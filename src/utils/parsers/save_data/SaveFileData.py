import typing

import pydantic


class SaveFileData(pydantic.BaseModel):

	shops: list[dict[str, typing.Any]]
