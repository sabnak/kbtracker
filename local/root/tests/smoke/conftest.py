import pytest
from pathlib import Path
from dependency_injector import providers
from unittest.mock import Mock

from src.core.Container import Container
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.SaveDataParser import SaveDataParser


@pytest.fixture(scope="session")
def test_saves_path() -> str:
	"""
	Session-scoped fixture for test save files path

	:return:
		Absolute path to test saves directory
	"""
	return str(Path(__file__).parent.parent / "game_files" / "saves")


@pytest.fixture(scope="session")
def test_save_1707047253_path(test_saves_path: str) -> Path:
	"""
	Session-scoped fixture for save file 1707047253

	:param test_saves_path:
		Base saves directory path
	:return:
		Absolute path to save directory
	"""
	return Path(test_saves_path) / "1707047253"


@pytest.fixture(scope="module")
def mock_item_repository():
	"""
	Module-scoped mock ItemRepository

	:return:
		Mock ItemRepository instance that always returns False
	"""
	mock_repo = Mock()
	mock_repo.is_item_exists.return_value = False
	return mock_repo


@pytest.fixture(scope="module")
def test_container(mock_item_repository):
	"""
	Module-scoped test container with real parser implementations

	:param mock_item_repository:
		Mock ItemRepository instance
	:return:
		Configured Container instance
	"""
	container = Container()

	container.save_file_decompressor.override(providers.Singleton(SaveFileDecompressor))
	container.save_data_parser.override(providers.Singleton(SaveDataParser))
	container.item_repository.override(providers.Singleton(lambda: mock_item_repository))

	container.wire(modules=["tests.smoke.test_save_data_parser"])

	yield container

	container.unwire()


@pytest.fixture
def save_data_parser(test_container):
	"""
	Function-scoped SaveDataParser instance

	:param test_container:
		Module-scoped test container
	:return:
		SaveDataParser instance from container
	"""
	return test_container.save_data_parser()
