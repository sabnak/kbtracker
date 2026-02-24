from typing import Annotated
from pydantic import BeforeValidator


def empty_str_to_none(v):
	"""
	Convert empty strings to None for optional query parameters

	:param v:
		Value to convert
	:return:
		None if empty string, otherwise original value
	"""
	if v == "" or v is None:
		return None
	return v


OptionalInt = Annotated[int | None, BeforeValidator(empty_str_to_none)]
