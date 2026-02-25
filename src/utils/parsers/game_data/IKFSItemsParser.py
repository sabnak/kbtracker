import abc


class IKFSItemsParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, game_id: int) -> dict[str, dict[str, any]]:
		...