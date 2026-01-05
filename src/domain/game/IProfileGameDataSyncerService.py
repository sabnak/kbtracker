import abc


class IProfileGameDataSyncerService(abc.ABC):

	@abc.abstractmethod
	def sync(self, profile_id: str, game_data: dict):
		...