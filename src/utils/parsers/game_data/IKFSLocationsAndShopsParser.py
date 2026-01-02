import abc

from src.domain.game.entities.Location import Location
from src.domain.game.entities.Shop import Shop


class IKFSLocationsAndShopsParser(abc.ABC):

	def parse(self, game_name: str, lang: str = 'rus') -> list[dict[str, Location | list[Shop]]]:
		...
