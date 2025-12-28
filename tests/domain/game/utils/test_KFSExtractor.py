import pytest
import os
from pathlib import Path
from src.domain.game.utils.KFSExtractor import KFSExtractor


class TestKFSExtractor:

	@staticmethod
	def _get_sessions_path() -> str:
		"""Get sessions path relative to project root"""
		return str(Path(__file__).parent.parent.parent.parent.parent / "tests" / "game_files" / "sessions")

	def test_extract_single_file(self):
		"""
		Test extracting a single file from archive
		"""
		sessions_path = self._get_sessions_path()
		tables = ["ses.kfs/items.txt"]

		extractor = KFSExtractor(sessions_path, tables)
		results = extractor.extract()

		assert len(results) == 1
		assert isinstance(results[0], str)
		assert len(results[0]) > 0
		assert "snake_belt" in results[0]

	def test_extract_multiple_files(self):
		"""
		Test extracting multiple files in correct order
		"""
		sessions_path = self._get_sessions_path()
		tables = ["ses.kfs/items.txt", "loc_ses.kfs/rus_items.lng"]

		extractor = KFSExtractor(sessions_path, tables)
		results = extractor.extract()

		assert len(results) == 2
		assert isinstance(results[0], str)
		assert isinstance(results[1], str)
		assert "snake_belt" in results[0]
		assert "itm_" in results[1]

	def test_extract_with_encoding(self):
		"""
		Test UTF-16 LE decoding with Russian characters
		"""
		sessions_path = self._get_sessions_path()
		tables = ["loc_ses.kfs/rus_items.lng"]

		extractor = KFSExtractor(sessions_path, tables)
		results = extractor.extract()

		assert len(results) == 1
		content = results[0]
		assert "itm_snake_belt_name" in content
		assert len(content) > 0

	def test_archive_not_found(self):
		"""
		Test error when archive doesn't exist
		"""
		sessions_path = self._get_sessions_path()
		tables = ["nonexistent.kfs/some_file.txt"]

		extractor = KFSExtractor(sessions_path, tables)

		with pytest.raises(FileNotFoundError) as exc_info:
			extractor.extract()

		assert "nonexistent.kfs" in str(exc_info.value)

	def test_file_not_in_archive(self):
		"""
		Test error when file doesn't exist in archive
		"""
		sessions_path = self._get_sessions_path()
		tables = ["ses.kfs/nonexistent_file.txt"]

		extractor = KFSExtractor(sessions_path, tables)

		with pytest.raises(KeyError) as exc_info:
			extractor.extract()

		assert "nonexistent_file.txt" in str(exc_info.value)

	def test_empty_tables_list(self):
		"""
		Test extracting with empty tables list
		"""
		sessions_path = self._get_sessions_path()
		tables = []

		extractor = KFSExtractor(sessions_path, tables)
		results = extractor.extract()

		assert results == []

	def test_invalid_sessions_path(self):
		"""
		Test error when sessions directory doesn't exist
		"""
		sessions_path = "/nonexistent_directory"
		tables = ["ses.kfs/items.txt"]

		extractor = KFSExtractor(sessions_path, tables)

		with pytest.raises(FileNotFoundError) as exc_info:
			extractor.extract()

		assert "Sessions directory not found" in str(exc_info.value)
