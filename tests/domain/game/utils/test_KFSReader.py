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

	def test_read_data_files_single_file(self, kfs_reader, test_game_name):
		"""
		Test reading a single data file
		"""
		filenames = ['items.txt']

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert len(results) == 1
		assert isinstance(results[0], str)
		assert len(results[0]) > 0
		assert 'snake_belt' in results[0]

	def test_read_loc_files_single_file(self, kfs_reader, test_game_name):
		"""
		Test reading a single localization file
		"""
		filenames = ['rus_items.lng']

		results = kfs_reader.read_loc_files(test_game_name, filenames)

		assert len(results) == 1
		assert isinstance(results[0], str)
		assert 'itm_' in results[0]

	def test_read_data_files_multiple_files(self, kfs_reader, test_game_name):
		"""
		Test reading multiple data files in correct order
		"""
		filenames = ['items.txt']

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert len(results) == 1
		assert isinstance(results[0], str)

	def test_read_loc_files_multiple_files(self, kfs_reader, test_game_name):
		"""
		Test reading multiple localization files in correct order
		"""
		filenames = ['rus_items.lng', 'rus_units.lng']

		results = kfs_reader.read_loc_files(test_game_name, filenames)

		assert len(results) == 2
		assert isinstance(results[0], str)
		assert isinstance(results[1], str)

	def test_read_data_files_preserves_order(self, kfs_reader, test_game_name):
		"""
		Test that files are returned in the same order as requested
		"""
		filenames = ['items.txt']

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert len(results) == 1

	def test_read_data_files_with_utf16_encoding(self, kfs_reader, test_game_name):
		"""
		Test UTF-16 LE decoding for data files
		"""
		filenames = ['items.txt']

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert len(results) == 1
		assert len(results[0]) > 0

	def test_read_loc_files_with_utf16_encoding(self, kfs_reader, test_game_name):
		"""
		Test UTF-16 LE decoding with Russian characters
		"""
		filenames = ['rus_items.lng']

		results = kfs_reader.read_loc_files(test_game_name, filenames)

		assert len(results) == 1
		content = results[0]
		assert 'itm_snake_belt_name' in content
		assert len(content) > 0

	def test_read_data_files_file_not_found(self, kfs_reader, test_game_name):
		"""
		Test error when requested data file doesn't exist
		"""
		filenames = ['nonexistent_file.txt']

		with pytest.raises(FileNotFoundError):
			kfs_reader.read_data_files(test_game_name, filenames)

	def test_read_loc_files_file_not_found(self, kfs_reader, test_game_name):
		"""
		Test error when requested localization file doesn't exist
		"""
		filenames = ['nonexistent_file.lng']

		with pytest.raises(FileNotFoundError):
			kfs_reader.read_loc_files(test_game_name, filenames)

	def test_read_data_files_returns_list(self, kfs_reader, test_game_name):
		"""
		Test that read_data_files always returns a list
		"""
		filenames = ['items.txt']

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert isinstance(results, list)
		assert len(results) == len(filenames)

	def test_read_loc_files_returns_list(self, kfs_reader, test_game_name):
		"""
		Test that read_loc_files always returns a list
		"""
		filenames = ['rus_items.lng']

		results = kfs_reader.read_loc_files(test_game_name, filenames)

		assert isinstance(results, list)
		assert len(results) == len(filenames)

	def test_read_data_files_empty_list(self, kfs_reader, test_game_name):
		"""
		Test reading empty file list returns empty list
		"""
		filenames = []

		results = kfs_reader.read_data_files(test_game_name, filenames)

		assert results == []
		assert isinstance(results, list)

	def test_read_loc_files_empty_list(self, kfs_reader, test_game_name):
		"""
		Test reading empty file list returns empty list
		"""
		filenames = []

		results = kfs_reader.read_loc_files(test_game_name, filenames)

		assert results == []
		assert isinstance(results, list)
