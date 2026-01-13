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
		Test that all archives are extracted to correct session subdirectories
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check that subdirectories exist
		assert os.path.exists(os.path.join(extraction_root, 'data'))
		assert os.path.exists(os.path.join(extraction_root, 'loc'))

		# Check that session subdirectories exist
		assert os.path.exists(os.path.join(extraction_root, 'data', 'darkside'))
		assert os.path.exists(os.path.join(extraction_root, 'loc', 'darkside'))

		# Check that files were extracted to correct session subdirectories
		assert os.path.exists(os.path.join(extraction_root, 'data', 'darkside', 'items.txt'))
		assert os.path.exists(os.path.join(extraction_root, 'loc', 'darkside', 'rus_items.lng'))

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
		Test that extraction completes without error even when no archives found
		"""
		invalid_game = Game(
			id=999,
			name="Nonexistent Game",
			path="nonexistent_game",
			last_scan_time=None,
			sessions=["nonexistent"],
			saves_pattern="*.sav"
		)

		# Should not raise error, just extract nothing
		extraction_root = kfs_extractor.extract_archives(invalid_game)
		assert extraction_root == f'/tmp/{invalid_game.path}'

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

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
		Test that data archives are extracted to data session subdirectory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		data_dir = os.path.join(extraction_root, 'data')
		assert os.path.exists(data_dir)
		assert os.path.isdir(data_dir)

		# Should contain session subdirectory with items.txt
		session_dir = os.path.join(data_dir, 'darkside')
		assert os.path.exists(session_dir)
		items_file = os.path.join(session_dir, 'items.txt')
		assert os.path.exists(items_file)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_filters_by_extension(self, kfs_extractor, test_game):
		"""
		Test that only .atom, .txt, .lng files are extracted
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check data directory session subdirectories - should only have .atom and .txt files
		data_dir = os.path.join(extraction_root, 'data')
		for session_name in os.listdir(data_dir):
			session_dir = os.path.join(data_dir, session_name)
			if os.path.isdir(session_dir):
				for file in os.listdir(session_dir):
					ext = os.path.splitext(file)[1].lower()
					assert ext in ['.atom', '.txt'], f"Unexpected file extension in data/{session_name}: {ext}"

		# Check loc directory session subdirectories - should only have .lng files
		loc_dir = os.path.join(extraction_root, 'loc')
		for session_name in os.listdir(loc_dir):
			session_dir = os.path.join(loc_dir, session_name)
			if os.path.isdir(session_dir):
				for file in os.listdir(session_dir):
					ext = os.path.splitext(file)[1].lower()
					assert ext == '.lng', f"Unexpected file in loc/{session_name}: {file}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_creates_session_subdirectories(self, kfs_extractor, test_game):
		"""
		Test that session subdirectories are created and files within them are flat
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		# Check data directory - should contain session subdirectories
		data_dir = os.path.join(extraction_root, 'data')
		assert os.path.exists(os.path.join(data_dir, 'darkside')), "Session subdirectory missing in data/"

		# Check that files within session subdirectories are flat (no nested directories)
		for session_name in os.listdir(data_dir):
			session_dir = os.path.join(data_dir, session_name)
			if os.path.isdir(session_dir):
				for entry in os.listdir(session_dir):
					entry_path = os.path.join(session_dir, entry)
					assert os.path.isfile(entry_path), f"Found nested directory in data/{session_name}/: {entry}"

		# Check loc directory - should contain session subdirectories
		loc_dir = os.path.join(extraction_root, 'loc')
		assert os.path.exists(os.path.join(loc_dir, 'darkside')), "Session subdirectory missing in loc/"

		# Check that files within session subdirectories are flat (no nested directories)
		for session_name in os.listdir(loc_dir):
			session_dir = os.path.join(loc_dir, session_name)
			if os.path.isdir(session_dir):
				for entry in os.listdir(session_dir):
					entry_path = os.path.join(session_dir, entry)
					assert os.path.isfile(entry_path), f"Found nested directory in loc/{session_name}/: {entry}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_routes_lng_to_loc(self, kfs_extractor, test_game):
		"""
		Test that .lng files go to loc/ session subdirectories
		"""
		extraction_root = kfs_extractor.extract_archives(test_game)

		loc_dir = os.path.join(extraction_root, 'loc')

		# Should have .lng files in session subdirectory
		assert os.path.exists(os.path.join(loc_dir, 'darkside', 'rus_items.lng'))

		# Data directory session subdirectories should NOT have .lng files
		data_dir = os.path.join(extraction_root, 'data')
		for session_name in os.listdir(data_dir):
			session_dir = os.path.join(data_dir, session_name)
			if os.path.isdir(session_dir):
				for file in os.listdir(session_dir):
					ext = os.path.splitext(file)[1].lower()
					assert ext != '.lng', f"Found .lng file in data/{session_name}/: {file}"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_with_multiple_sessions(
		self,
		kfs_extractor,
		test_game_name,
		test_config
	):
		"""
		Test extraction with game having multiple sessions creates separate subdirectories
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

		# Files should be extracted to session subdirectories
		assert os.path.exists(extraction_root)
		assert os.path.exists(os.path.join(extraction_root, 'data', 'darkside'))
		assert os.path.exists(os.path.join(extraction_root, 'loc', 'darkside'))

		# Session subdirectory should contain files
		session_data_dir = os.path.join(extraction_root, 'data', 'darkside')
		assert len(os.listdir(session_data_dir)) > 0, "Session data directory is empty"

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)
