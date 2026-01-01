import pytest


class TestKFSExtractor:

	def test_extract_single_file(self, kfs_extractor, test_sessions_path):
		"""
		Test extracting a single file from archive
		"""
		tables = ["ses.kfs/items.txt"]

		results = kfs_extractor.extract(test_sessions_path, tables)

		assert len(results) == 1
		assert isinstance(results[0], str)
		assert len(results[0]) > 0
		assert "snake_belt" in results[0]

	def test_extract_multiple_files(self, kfs_extractor, test_sessions_path):
		"""
		Test extracting multiple files in correct order
		"""
		tables = ["ses.kfs/items.txt", "loc_ses.kfs/rus_items.lng"]

		results = kfs_extractor.extract(test_sessions_path, tables)

		assert len(results) == 2
		assert isinstance(results[0], str)
		assert isinstance(results[1], str)
		assert "snake_belt" in results[0]
		assert "itm_" in results[1]

	def test_extract_with_encoding(self, kfs_extractor, test_sessions_path):
		"""
		Test UTF-16 LE decoding with Russian characters
		"""
		tables = ["loc_ses.kfs/rus_items.lng"]

		results = kfs_extractor.extract(test_sessions_path, tables)

		assert len(results) == 1
		content = results[0]
		assert "itm_snake_belt_name" in content
		assert len(content) > 0

	def test_archive_not_found(self, kfs_extractor, test_sessions_path):
		"""
		Test error when archive doesn't exist
		"""
		tables = ["nonexistent.kfs/some_file.txt"]

		with pytest.raises(FileNotFoundError) as exc_info:
			kfs_extractor.extract(test_sessions_path, tables)

		assert "nonexistent.kfs" in str(exc_info.value)

	def test_file_not_in_archive(self, kfs_extractor, test_sessions_path):
		"""
		Test error when file doesn't exist in archive
		"""
		tables = ["ses.kfs/nonexistent_file.txt"]

		with pytest.raises(KeyError) as exc_info:
			kfs_extractor.extract(test_sessions_path, tables)

		assert "nonexistent_file.txt" in str(exc_info.value)

	def test_empty_tables_list(self, kfs_extractor, test_sessions_path):
		"""
		Test extracting with empty tables list
		"""
		tables = []

		results = kfs_extractor.extract(test_sessions_path, tables)

		assert results == []

	def test_invalid_sessions_path(self, kfs_extractor):
		"""
		Test error when sessions directory doesn't exist
		"""
		sessions_path = "/nonexistent_directory"
		tables = ["ses.kfs/items.txt"]

		with pytest.raises(FileNotFoundError) as exc_info:
			kfs_extractor.extract(sessions_path, tables)

		assert "Sessions directory not found" in str(exc_info.value)
