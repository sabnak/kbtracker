import abc
import re

from src.domain.game.entities.Localization import Localization


class IKFSLocalizationParser(abc.ABC):

	@abc.abstractmethod
	def parse(
		self,
		game_name: str,
		file_name: str,
		kb_id_pattern: re.Pattern = None,
		lang: str = 'rus',
		tag: str | None = None
	) -> dict[str, Localization]:
		...
