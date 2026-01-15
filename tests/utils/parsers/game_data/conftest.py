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
def test_game(test_game_name):
	"""
	Session-scoped fixture for test Game object

	:param test_game_name:
		Test game name
	:return:
		Test Game entity
	"""
	from src.domain.app.entities.Game import Game
	from datetime import datetime

	return Game(
		id=1,
		name="Test Game",
		path=test_game_name,
		last_scan_time=datetime.now(),
		sessions=["darkside"],
		saves_pattern="*.sav"
	)


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
	# Exclude data.kfs from tests - it's large and slows down test execution
	# Test patterns point to sessions/{session}/ structure
	config.data_archive_path = "{game_path}/data/data.kfs"
	config.session_archives_pattern = "{game_path}/darkside/*.kfs"
	config.tmp_dir = "/tmp"
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

	container.wire(packages=[
		"tests.utils.parsers.game_data"
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
def kfs_atoms_map_info_parser(test_container):
	"""
	Function-scoped KFSAtomsMapInfoParser instance

	:return:
		KFSAtomsMapInfoParser instance from container
	"""
	return test_container.kfs_atoms_map_info_parser()


@pytest.fixture
def extracted_game_files(kfs_extractor, test_game):
	"""
	Fixture that extracts game archives before tests and cleans up after

	:param kfs_extractor:
		KFSExtractor instance
	:param test_game:
		Test Game entity
	:return:
		Extraction root path
	"""
	import shutil

	# Extract archives
	extraction_root = kfs_extractor.extract_archives(test_game)

	yield extraction_root

	# Cleanup
	shutil.rmtree(extraction_root, ignore_errors=True)
