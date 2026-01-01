import abc
from pathlib import Path


class ICampaignIdentifierParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, save_path: Path) -> dict[str, str]:
		"""
		Extract campaign identifier from save file

		:param save_path:
			Path to save 'data' file
		:return:
			Dictionary with campaign_id, first_name, second_name, full_name
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		...
