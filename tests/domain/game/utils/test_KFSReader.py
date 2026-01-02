import os
import pytest
import shutil


class TestKFSReader:

	@pytest.fixture(autouse=True)
	def setup_extraction(self, kfs_extractor, test_game_name):
		"""
		Auto-use fixture that extracts archives before each test

		:param kfs_extractor:
			KFSExtractor instance
		:param test_game_name:
			Test game name
		"""
		# Extract archives for tests
		kfs_extractor.extract_archives(test_game_name)

		yield

		# Cleanup after test
		extraction_root = f'/tmp/{test_game_name}'
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_read_single_file(self, kfs_reader, test_game_name):
		"""
		Test reading a single file from extracted directory
		"""
		file_paths = ['ses/items.txt']

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert len(results) == 1
		assert isinstance(results[0], str)
		assert len(results[0]) > 0
		assert 'snake_belt' in results[0]

	def test_read_multiple_files(self, kfs_reader, test_game_name):
		"""
		Test reading multiple files in correct order
		"""
		file_paths = ['ses/items.txt', 'loc_ses/rus_items.lng']

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert len(results) == 2
		assert isinstance(results[0], str)
		assert isinstance(results[1], str)
		assert 'snake_belt' in results[0]
		assert 'itm_' in results[1]

	def test_read_files_preserves_order(self, kfs_reader, test_game_name):
		"""
		Test that files are returned in the same order as requested
		"""
		file_paths = ['loc_ses/rus_items.lng', 'ses/items.txt']

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert len(results) == 2
		# First result should be from loc_ses (contains 'itm_')
		assert 'itm_' in results[0]
		# Second result should be from ses (contains 'snake_belt')
		assert 'snake_belt' in results[1]

	def test_read_files_with_utf16_encoding(self, kfs_reader, test_game_name):
		"""
		Test UTF-16 LE decoding with Russian characters
		"""
		file_paths = ['loc_ses/rus_items.lng']

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert len(results) == 1
		content = results[0]
		assert 'itm_snake_belt_name' in content
		assert len(content) > 0

	def test_read_files_file_not_found(self, kfs_reader, test_game_name):
		"""
		Test error when requested file doesn't exist
		"""
		file_paths = ['ses/nonexistent_file.txt']

		with pytest.raises(FileNotFoundError):
			kfs_reader.read_files(test_game_name, file_paths)

	def test_read_files_returns_list(self, kfs_reader, test_game_name):
		"""
		Test that read_files always returns a list
		"""
		file_paths = ['ses/items.txt']

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert isinstance(results, list)
		assert len(results) == len(file_paths)

	def test_read_files_empty_list(self, kfs_reader, test_game_name):
		"""
		Test reading empty file list returns empty list
		"""
		file_paths = []

		results = kfs_reader.read_files(test_game_name, file_paths)

		assert results == []
		assert isinstance(results, list)
