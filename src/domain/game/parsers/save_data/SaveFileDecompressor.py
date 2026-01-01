from pathlib import Path
import struct
import zlib

from src.domain.game.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class SaveFileDecompressor(ISaveFileDecompressor):

	MAGIC_HEADER: bytes = b'slcb'
	HEADER_SIZE: int = 12

	def decompress(self, save_path: Path) -> bytes:
		"""
		Decompress King's Bounty save data file

		Save file format:
		- 4 bytes: Magic "slcb"
		- 4 bytes: Decompressed size (uint32 LE)
		- 4 bytes: Compressed size (uint32 LE)
		- N bytes: zlib compressed data

		:param save_path:
			Path to save 'data' file
		:return:
			Decompressed binary data
		:raises ValueError:
			If magic header invalid or size mismatch
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		self._validate_file_exists(save_path)

		with open(save_path, 'rb') as f:
			data = f.read()

		magic = data[0:4]
		self._validate_magic_header(magic)

		decompressed_size = struct.unpack('<I', data[4:8])[0]
		compressed_size = struct.unpack('<I', data[8:12])[0]

		compressed_data = data[12:12 + compressed_size]
		decompressed_data = zlib.decompress(compressed_data)

		self._validate_decompressed_size(decompressed_data, decompressed_size)

		return decompressed_data

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
