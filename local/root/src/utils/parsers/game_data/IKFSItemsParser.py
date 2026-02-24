import abc


class IKFSItemsParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, game_name: str) -> dict[str, dict[str, any]]:
		...