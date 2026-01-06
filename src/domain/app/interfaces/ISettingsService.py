import abc

from src.domain.app.entities.Settings import Settings


class ISettingsService(abc.ABC):

	@abc.abstractmethod
	def get_settings(self) -> Settings:
		...

	@abc.abstractmethod
	def save_settings(self, settings: Settings) -> None:
		...
