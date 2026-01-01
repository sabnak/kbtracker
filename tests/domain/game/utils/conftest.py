import pytest
from pathlib import Path
from dependency_injector import providers

from src.core.Container import Container
from src.utils.parsers.game_data import KFSExtractor
from src.utils.parsers.game_data.KFSItemsParser import KFSItemsParser
from src.utils.parsers.game_data.KFSLocalizationParser import KFSLocalizationParser
from src.utils.parsers.game_data import KFSLocationsAndShopsParser


@pytest.fixture(scope="session")
def test_sessions_path() -> str:
	"""
	Session-scoped fixture for test game files path

	:return:
		Absolute path to test sessions directory
	"""
	return str(Path(__file__).parent.parent.parent.parent / "game_files" / "sessions")


@pytest.fixture(scope="module")
def test_container():
	"""
	Module-scoped test container with real parser implementations

	:return:
		Configured Container instance
	"""
	container = Container()

	container.kfs_extractor.override(providers.Singleton(KFSExtractor))
	container.kfs_items_parser.override(providers.Singleton(KFSItemsParser))
	container.kfs_localization_parser.override(providers.Singleton(KFSLocalizationParser))
	container.kfs_locations_and_shops_parser.override(providers.Singleton(KFSLocationsAndShopsParser))

	container.wire(modules=[
		"tests.domain.game.utils.test_KFSExtractor",
		"tests.domain.game.utils.test_KFSItemsParser",
		"tests.domain.game.utils.test_KFSLocalizationParser",
		"tests.domain.game.utils.test_KFSLocationsAndShopsParser"
	])

	yield container

	container.unwire()


@pytest.fixture
def kfs_extractor(test_container):
	"""
	Function-scoped KFSExtractor instance

	:return:
		KFSExtractor instance from container
	"""
	return test_container.kfs_extractor()


@pytest.fixture
def kfs_items_parser(test_container):
	"""
	Function-scoped KFSItemsParser instance

	:return:
		KFSItemsParser instance from container
	"""
	return test_container.kfs_items_parser()


@pytest.fixture
def kfs_localization_parser(test_container):
	"""
	Function-scoped KFSLocalizationParser instance

	:return:
		KFSLocalizationParser instance from container
	"""
	return test_container.kfs_localization_parser()


@pytest.fixture
def kfs_locations_and_shops_parser(test_container):
	"""
	Function-scoped KFSLocationsAndShopsParser instance

	:return:
		KFSLocalizationParser instance from container
	"""
	return test_container.kfs_locations_and_shops_parser()
