import abc

from src.domain.game.entities.AtomMap import AtomMap


class IKFSAtomsMapInfoParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, game_name: str, lang: str = 'rus') -> list[AtomMap]:
		pass
