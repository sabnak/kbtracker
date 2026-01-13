import abc
from pathlib import Path


class ISaveFileDecompressor(abc.ABC):

	@abc.abstractmethod
	def decompress(self, save_path: Path) -> bytes:
		"""
		Decompress King's Bounty save data file

		:param save_path:
			Path to save (directory containing 'data' file or .sav archive)
		:return:
			Decompressed binary data
		:raises ValueError:
			If save file format is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
