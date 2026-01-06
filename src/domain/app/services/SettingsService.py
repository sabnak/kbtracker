from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.domain.app.entities.MetaName import MetaName
from src.domain.app.entities.Settings import Settings
from src.domain.app.interfaces.IMetaRepository import IMetaRepository
from src.domain.app.interfaces.ISettingsService import ISettingsService
from src.domain.exceptions import MetadataNotFoundException


class SettingsService(ISettingsService):

	@inject
	def __init__(
		self,
		meta_repository: IMetaRepository = Provide[Container.meta_repository]
	):
		self._meta_repository = meta_repository

	def get_settings(self) -> Settings:
		try:
			return self._meta_repository.get(MetaName.SETTINGS)
		except MetadataNotFoundException:
			return Settings()

	def save_settings(self, settings: Settings) -> None:
		self._meta_repository.save(MetaName.SETTINGS, settings)
