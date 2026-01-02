import os
import pytest
import shutil


class TestKFSExtractor:

	def test_extract_archives_creates_extraction_root(self, kfs_extractor, test_game_name):
		"""
		Test that extract_archives creates extraction root directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game_name)

		assert extraction_root == f'/tmp/{test_game_name}'
		assert os.path.exists(extraction_root)
		assert os.path.isdir(extraction_root)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_extracts_all_archives(self, kfs_extractor, test_game_name):
		"""
		Test that all archives are extracted to correct directories
		"""
		extraction_root = kfs_extractor.extract_archives(test_game_name)

		# Check that subdirectories exist
		assert os.path.exists(os.path.join(extraction_root, 'data'))
		assert os.path.exists(os.path.join(extraction_root, 'loc'))

		# Check that files were extracted to correct locations
		assert os.path.exists(os.path.join(extraction_root, 'data', 'items.txt'))
		assert os.path.exists(os.path.join(extraction_root, 'loc', 'rus_items.lng'))

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_returns_correct_path(self, kfs_extractor, test_game_name):
		"""
		Test that extract_archives returns correct extraction root path
		"""
		result = kfs_extractor.extract_archives(test_game_name)

		assert result == f'/tmp/{test_game_name}'
		assert isinstance(result, str)

		# Cleanup
		shutil.rmtree(result, ignore_errors=True)

	def test_extract_archives_cleanup_previous_extraction(self, kfs_extractor, test_game_name):
		"""
		Test that previous extraction is cleaned up before new extraction
		"""
		extraction_root = f'/tmp/{test_game_name}'

		# Create a fake previous extraction with a marker file
		os.makedirs(extraction_root, exist_ok=True)
		marker_file = os.path.join(extraction_root, 'old_marker.txt')
		with open(marker_file, 'w') as f:
			f.write('old extraction')

		# Run extraction
		kfs_extractor.extract_archives(test_game_name)

		# Marker file should be gone (cleanup happened)
		assert not os.path.exists(marker_file)
		assert os.path.exists(extraction_root)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_with_invalid_game_name(self, kfs_extractor):
		"""
		Test error when game directory doesn't exist
		"""
		with pytest.raises(FileNotFoundError):
			kfs_extractor.extract_archives("nonexistent_game")

	def test_extract_archives_creates_loc_directory(self, kfs_extractor, test_game_name):
		"""
		Test that localization archives are extracted to loc directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game_name)

		loc_dir = os.path.join(extraction_root, 'loc')
		assert os.path.exists(loc_dir)
		assert os.path.isdir(loc_dir)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)

	def test_extract_archives_creates_data_directory(self, kfs_extractor, test_game_name):
		"""
		Test that data archives are extracted to data directory
		"""
		extraction_root = kfs_extractor.extract_archives(test_game_name)

		data_dir = os.path.join(extraction_root, 'data')
		assert os.path.exists(data_dir)
		assert os.path.isdir(data_dir)

		# Should contain items.txt from ses archives
		items_file = os.path.join(data_dir, 'items.txt')
		assert os.path.exists(items_file)

		# Cleanup
		shutil.rmtree(extraction_root, ignore_errors=True)
