import abc
import enum
from pathlib import Path

from src.utils.parsers.save_data.DataFileType import DataFileType


class ISaveFileDecompressor(abc.ABC):

	@abc.abstractmethod
	def decompress(self, save_path: Path, data_type: DataFileType = DataFileType.DATA) -> bytes:
		"""
		Decompress King's Bounty save data file

		:param save_path:
			Path to save (directory containing 'data' file or .sav archive)
		:param data_type:
			File type to extract
		:return:
			Decompressed binary data
		:raises ValueError:
			If save file format is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
