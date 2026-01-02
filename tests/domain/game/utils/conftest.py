import pytest
from pathlib import Path
from dependency_injector import providers
from unittest.mock import Mock

from src.core.Container import Container
from src.core.Config import Config
from src.utils.parsers.game_data.KFSExtractor import KFSExtractor
from src.utils.parsers.game_data.KFSReader import KFSReader
from src.utils.parsers.game_data.KFSItemsParser import KFSItemsParser
from src.utils.parsers.game_data.KFSLocalizationParser import KFSLocalizationParser
from src.utils.parsers.game_data.KFSLocationsAndShopsParser import KFSLocationsAndShopsParser


@pytest.fixture(scope="session")
def test_sessions_path() -> str:
	"""
	Session-scoped fixture for test game files path

	:return:
		Absolute path to test sessions directory
	"""
	return str(Path(__file__).parent.parent.parent.parent / "game_files" / "sessions")


@pytest.fixture(scope="session")
def test_game_data_path() -> str:
	"""
	Session-scoped fixture for test game data root path

	:return:
		Absolute path to test data directory
	"""
	return str(Path(__file__).parent.parent.parent.parent / "game_files" / "tests")


@pytest.fixture(scope="session")
def test_game_name() -> str:
	"""
	Session-scoped fixture for test game name

	:return:
		Test game name (corresponds to sessions directory)
	"""
	return "sessions"


@pytest.fixture(scope="session")
def test_config(test_game_data_path):
	"""
	Session-scoped mock Config for tests

	:param test_game_data_path:
		Path to test game data root
	:return:
		Mock Config instance
	"""
	config = Mock(spec=Config)
	config.game_data_path = test_game_data_path
	# Test pattern points directly to darkside directory
	# Exclude data.kfs from tests - it's large and slows down test execution
	config.archive_patterns = [
		"{game_path}/darkside/*.kfs"
	]
	return config


@pytest.fixture(scope="module")
def test_container(test_config):
	"""
	Module-scoped test container with real parser implementations

	:param test_config:
		Mock Config instance for tests
	:return:
		Configured Container instance
	"""
	container = Container()

	container.config.override(providers.Singleton(lambda: test_config))
	container.kfs_extractor.override(providers.Singleton(KFSExtractor))
	container.kfs_reader.override(providers.Singleton(KFSReader))
	container.kfs_items_parser.override(providers.Singleton(KFSItemsParser))
	container.kfs_localization_parser.override(providers.Singleton(KFSLocalizationParser))
	container.kfs_locations_and_shops_parser.override(providers.Singleton(KFSLocationsAndShopsParser))

	container.wire(modules=[
		"tests.domain.game.utils.test_KFSExtractor",
		"tests.domain.game.utils.test_KFSReader",
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
def kfs_reader(test_container):
	"""
	Function-scoped KFSReader instance

	:return:
		KFSReader instance from container
	"""
	return test_container.kfs_reader()


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


@pytest.fixture
def extracted_game_files(kfs_extractor, test_game_name):
	"""
	Fixture that extracts game archives before tests and cleans up after

	:param kfs_extractor:
		KFSExtractor instance
	:param test_game_name:
		Test game name
	:return:
		Extraction root path
	"""
	import shutil

	# Extract archives
	extraction_root = kfs_extractor.extract_archives(test_game_name)

	yield extraction_root

	# Cleanup
	shutil.rmtree(extraction_root, ignore_errors=True)
