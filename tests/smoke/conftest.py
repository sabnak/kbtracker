import pytest
from pathlib import Path
from dependency_injector import providers

from src.core.Container import Container
from src.domain.game.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.domain.game.parsers.save_data.ShopInventoryParser import ShopInventoryParser


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
		Absolute path to save data file
	"""
	return Path(test_saves_path) / "1707047253" / "data"


@pytest.fixture(scope="module")
def test_container():
	"""
	Module-scoped test container with real parser implementations

	:return:
		Configured Container instance
	"""
	container = Container()

	container.save_file_decompressor.override(providers.Singleton(SaveFileDecompressor))
	container.shop_inventory_parser.override(providers.Singleton(ShopInventoryParser))

	container.wire(modules=["tests.smoke.test_shop_inventory_parser"])

	yield container

	container.unwire()


@pytest.fixture
def shop_inventory_parser(test_container):
	"""
	Function-scoped ShopInventoryParser instance

	:param test_container:
		Module-scoped test container
	:return:
		ShopInventoryParser instance from container
	"""
	return test_container.shop_inventory_parser()
