import abc


class IKFSItemsParser(abc.ABC):

	@abc.abstractmethod
	def parse(self, sessions_path: str) -> dict[str, dict[str, any]]:
		...