import typing
from pathlib import Path
import struct
import zlib
import zipfile
import tempfile
import shutil

from src.utils.parsers.save_data.DataFileType import DataFileType
from src.utils.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class SaveFileDecompressor(ISaveFileDecompressor):

	MAGIC_HEADER: bytes = b'slcb'
	HEADER_SIZE: int = 12

	_DATA_FILE_NAMES = ("data", "savedata")
	_INFO_FILE_NAMES = ("info", "saveinfo")

	def decompress(self, save_path: Path, data_type: DataFileType = DataFileType.DATA) -> bytes:
		"""
		Decompress King's Bounty save data file

		Save file format:
		- 4 bytes: Magic "slcb"
		- 4 bytes: Decompressed size (uint32 LE)
		- 4 bytes: Compressed size (uint32 LE)
		- N bytes: zlib compressed data

		:param save_path:
			Path to save
		:param data_type:
			File type to extract
		:return:
			Decompressed binary data
		:raises ValueError:
			If magic header invalid or size mismatch
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		if data_type == DataFileType.INFO:
			names = self._INFO_FILE_NAMES[:]
		else:
			names = self._DATA_FILE_NAMES[:]
		data = self._extract_data_file(save_path, names)

		magic = data[0:4]
		self._validate_magic_header(magic)

		decompressed_size = struct.unpack('<I', data[4:8])[0]
		compressed_size = struct.unpack('<I', data[8:12])[0]

		compressed_data = data[12:12 + compressed_size]
		decompressed_data = zlib.decompress(compressed_data)

		self._validate_decompressed_size(decompressed_data, decompressed_size)

		return decompressed_data

	def _extract_data_file(self, save_path: Path, file_names: typing.Iterable[str]) -> bytes:
		"""
		Extract 'data' file from save (directory or .sav archive)

		:param save_path:
			Path to save (directory or .sav file)
		:return:
			Raw bytes of 'data' file
		:raises FileNotFoundError:
			If save path or 'data' file doesn't exist
		:raises ValueError:
			If .sav archive is invalid or too large
		"""
		if not save_path.exists():
			raise FileNotFoundError(f"Save path not found: {save_path}")

		if save_path.suffix == '.sav':
			return self._extract_from_archive(save_path, file_names)
		else:
			return self._extract_from_directory(save_path, file_names)

	@staticmethod
	def _extract_from_directory(save_dir: Path, file_names: typing.Iterable[str]) -> bytes:
		"""
		Extract 'data' file from save directory

		:param save_dir:
			Path to directory containing 'data' file
		:return:
			Raw bytes of 'data' file
		:raises FileNotFoundError:
			If 'data' file doesn't exist
		"""
		data_files = [save_dir / n for n in file_names]
		for data_file in data_files:
			if not data_file.exists():
				continue
			with open(data_file, 'rb') as f:
				return f.read()
		raise FileNotFoundError(f"Data file not found in save directory: {save_dir}")

	@staticmethod
	def _extract_from_archive(archive_path: Path, file_names: typing.Iterable[str]) -> bytes:
		"""
		Extract 'data' file from .sav ZIP archive

		:param archive_path:
			Path to .sav archive file
		:return:
			Raw bytes of 'data' file
		:raises FileNotFoundError:
			If 'data' file not found in archive
		:raises ValueError:
			If archive is invalid or too large
		"""
		temp_dir = None
		try:
			if not zipfile.is_zipfile(archive_path):
				raise ValueError(f"Invalid ZIP archive: {archive_path}")

			temp_dir = tempfile.mkdtemp(prefix='kbsave_')
			temp_path = Path(temp_dir)

			with zipfile.ZipFile(archive_path, 'r') as zip_file:
				total_size = sum(info.file_size for info in zip_file.infolist())
				max_size = 10 * 1024 * 1024

				if total_size > max_size:
					raise ValueError(f"Archive too large: {total_size} bytes (max {max_size})")

				zip_file.extractall(temp_path)

			data_files = [temp_path / n for n in file_names]
			for data_file in data_files:
				if not data_file.exists():
					continue
				with open(data_file, 'rb') as f:
					return f.read()
			raise FileNotFoundError(f"'data' file not found in archive: {archive_path}")

		finally:
			if temp_dir and Path(temp_dir).exists():
				shutil.rmtree(temp_dir, ignore_errors=True)

	@staticmethod
	def _validate_file_exists(save_path: Path) -> None:
		"""
		Validate save file exists

		:param save_path:
			Path to validate
		:raises FileNotFoundError:
			If file doesn't exist
		"""
		if not save_path.exists():
			raise FileNotFoundError(f"Save file not found: {save_path}")

	@classmethod
	def _validate_magic_header(cls, magic: bytes) -> None:
		"""
		Validate magic header

		:param magic:
			Magic bytes to validate
		:raises ValueError:
			If magic doesn't match expected value
		"""
		if magic != cls.MAGIC_HEADER:
			raise ValueError(
				f"Invalid save file format. Expected '{cls.MAGIC_HEADER.decode()}', "
				f"got '{magic.decode()}'"
			)

	@staticmethod
	def _validate_decompressed_size(data: bytes, expected_size: int) -> None:
		"""
		Validate decompressed data size

		:param data:
			Decompressed data
		:param expected_size:
			Expected size from header
		:raises ValueError:
			If size mismatch
		"""
		if len(data) != expected_size:
			raise ValueError(
				f"Size mismatch after decompression. "
				f"Expected {expected_size}, got {len(data)}"
			)
