import abc
import logging
import typing

import pydantic
from dotenv import load_dotenv

from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller

T = typing.TypeVar("T", bound=pydantic.BaseModel)


class CLITool(typing.Generic[T], abc.ABC):

	_launch_params: T = None
	_container: Container = None
	_logger: logging.Logger = None

	def __init__(self):
		load_dotenv()
		self._launch_params = self._build_params()
		self._container = Container()
		installer = DefaultInstaller(self._container)
		installer.install()
		self._logger = self._container.logger()

	def run(self):
		self._run()

	@abc.abstractmethod
	def _build_params(self) -> T:
		...

	@abc.abstractmethod
	def _run(self):
		...


