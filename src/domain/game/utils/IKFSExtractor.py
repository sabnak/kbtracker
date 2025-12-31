import abc


class IKFSExtractor(abc.ABC):

	@abc.abstractmethod
	def extract(self, sessions_path: str, tables: list[str]) -> list[str]:
		...
