import abc
from pathlib import Path

from src.utils.parsers.save_data.SaveFileData import SaveFileData


class ISaveDataParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, save_path: Path) -> SaveFileData:
		"""
		Extract save file data including shop inventories

		:param save_path:
			Path to save 'data' file
		:return:
			SaveFileData containing parsed shop inventories
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
