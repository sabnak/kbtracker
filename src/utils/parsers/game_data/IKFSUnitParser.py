import abc

from src.domain.game.entities.Unit import Unit


class IKFSUnitParser(abc.ABC):

	@abc.abstractmethod
	def parse(
		self,
		game_name: str,
		allowed_kb_ids: list[str] | None = None
	) -> list[Unit]:
		"""
		Extract and parse unit data from game files

		:param game_name:
			Game name (e.g., 'Darkside', 'Armored_Princess')
		:param allowed_kb_ids:
			Optional list of unit kb_ids to parse (for testing)
			If None, parses all units found in localization
		:return:
			List of Unit entities with empty id and localized names
		:raises FileNotFoundError:
			When unit atom file not found
		"""
		...
