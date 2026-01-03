import abc
from pathlib import Path


class IHeroSaveParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, save_path: Path) -> dict[str, str]:
		"""
		Extract hero names from save file

		:param save_path:
			Path to save 'data' file
		:return:
			Dictionary with first_name and second_name
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
