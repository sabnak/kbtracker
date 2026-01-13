import os
import pytest
import shutil

from src.domain.app.entities.Game import Game
from datetime import datetime


class TestKFSExtractor:

	def test_extract_archives_creates_extraction_root(self, kfs_extractor, test_game):
		"""
		Test that extract_archives creates extraction root directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		assert extraction_root == f'/tmp/{test_game.path}'
		assert os.path.exists(extraction_root)
		assert os.path.isdir(extraction_root)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_extracts_all_archives(self, kfs_extractor, test_game):
		"""
		Test that all archives are extracted to correct directories
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check that subdirectories exist
		assert os.path.exists(os.path.join(extraction_root, 'data'))
		assert os.path.exists(os.path.join(extraction_root, 'loc'))

		# Check that files were extracted to correct locations
		assert os.path.exists(os.path.join(extraction_root, 'data', 'items.txt'))
		assert os.path.exists(os.path.join(extraction_root, 'loc', 'rus_items.lng'))

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_returns_correct_path(self, kfs_extractor, test_game):
		"""
		Test that extract_archives returns correct extraction root path
		"""
		result = kfs_extractor.extract_archives(test_game)

		assert result == f'/tmp/{test_game.path}'
		assert isinstance(result, str)

		# Cleanup
		shutil.rmtree(result, ignore_errors=True)

	def test_extract_archives_cleanup_previous_extraction(self, kfs_extractor, test_game):
		"""
		Test that previous extraction is cleaned up before new extraction
		"""
		extraction_root = f'/tmp/{test_game.path}'

		# Create a fake previous extraction with a marker file
		os.makedirs(extraction_root, exist_ok=True)
		marker_file = os.path.join(extraction_root, 'old_marker.txt')
		with open(marker_file, 'w') as f:
			f.write('old extraction')

		# Run extraction
		kfs_extractor.extract_archives(test_game)

		# Marker file should be gone (cleanup happened)
		assert not os.path.exists(marker_file)
		assert os.path.exists(extraction_root)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_with_invalid_game_path(self, kfs_extractor, test_config):
		"""
		Test error when game directory doesn't exist
		"""
		invalid_game = Game(
			id=999,
			name="Nonexistent Game",
			path="nonexistent_game",
			last_scan_time=None,
			sessions=["nonexistent"],
			saves_pattern="*.sav"
		)

		with pytest.raises(FileNotFoundError):
			kfs_extractor.extract_archives(invalid_game)

	def test_extract_archives_creates_loc_directory(self, kfs_extractor, test_game):
		"""
		Test that localization archives are extracted to loc directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		loc_dir = os.path.join(extraction_root, 'loc')
		assert os.path.exists(loc_dir)
		assert os.path.isdir(loc_dir)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_creates_data_directory(self, kfs_extractor, test_game):
		"""
		Test that data archives are extracted to data directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		data_dir = os.path.join(extraction_root, 'data')
		assert os.path.exists(data_dir)
		assert os.path.isdir(data_dir)

		# Should contain items.txt from ses archives
		items_file = os.path.join(data_dir, 'items.txt')
		assert os.path.exists(items_file)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_filters_by_extension(self, kfs_extractor, test_game):
		"""
		Test that only .atom, .txt, .lng files are extracted
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check data directory - should only have .atom and .txt files
		data_dir = os.path.join(extraction_root, 'data')
		for file in os.listdir(data_dir):
			ext = os.path.splitext(file)[1].lower()
			assert ext in ['.atom', '.txt'], f"Unexpected file extension: {ext}"

		# Check loc directory - should only have .lng files
		loc_dir = os.path.join(extraction_root, 'loc')
		for file in os.listdir(loc_dir):
			ext = os.path.splitext(file)[1].lower()
			assert ext == '.lng', f"Unexpected file in loc/: {file}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_creates_flat_structure(self, kfs_extractor, test_game):
		"""
		Test that files are extracted flat (no subdirectories in output)
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check data directory - all entries should be files, not directories
		data_dir = os.path.join(extraction_root, 'data')
		for entry in os.listdir(data_dir):
			entry_path = os.path.join(data_dir, entry)
			assert os.path.isfile(entry_path), f"Found directory in data/: {entry}"

		# Check loc directory - all entries should be files, not directories
		loc_dir = os.path.join(extraction_root, 'loc')
		for entry in os.listdir(loc_dir):
			entry_path = os.path.join(loc_dir, entry)
			assert os.path.isfile(entry_path), f"Found directory in loc/: {entry}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_routes_lng_to_loc(self, kfs_extractor, test_game):
		"""
		Test that .lng files go to loc/ directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		loc_dir = os.path.join(extraction_root, 'loc')

		# Should have .lng files
		assert os.path.exists(os.path.join(loc_dir, 'rus_items.lng'))

		# Data directory should NOT have .lng files
		data_dir = os.path.join(extraction_root, 'data')
		for file in os.listdir(data_dir):
			ext = os.path.splitext(file)[1].lower()
			assert ext != '.lng', f"Found .lng file in data/: {file}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_with_multiple_sessions(
		self,
		kfs_extractor,
		test_game_name,
		test_config
	):
		"""
		Test extraction with game having multiple sessions
		"""
		# Create game with multiple sessions
		multi_session_game = Game(
			id=1,
			name="Multi-Session Game",
			path=test_game_name,
			last_scan_time=datetime.now(),
			sessions=["darkside"],
			saves_pattern="*.sav"
		)

		extraction_root = kfs_extractor.extract_archives(multi_session_game)

		# Files should be extracted
		assert os.path.exists(extraction_root)
		assert os.path.exists(os.path.join(extraction_root, 'data'))
		assert os.path.exists(os.path.join(extraction_root, 'loc'))

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)
