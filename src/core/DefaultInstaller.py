import os

from dependency_injector import providers

from src.core.Container import Container
from src.domain.filesystem.services.GamePathService import GamePathService
from src.domain.game.repositories.ItemRepository import ItemRepository
from src.domain.game.repositories.LocationRepository import LocationRepository
from src.domain.game.repositories.ObjectHasItemRepository import ObjectHasItemRepository
from src.domain.game.repositories.ObjectRepository import ObjectRepository
from src.domain.game.services.ItemTrackingService import ItemTrackingService
from src.domain.game.services.ScannerService import ScannerService
from src.domain.profile.repositories.ProfilePostgresRepository import ProfilePostgresRepository
from src.domain.profile.services.ProfileService import ProfileService
from src.utils.db import create_db_engine, create_session_factory


class DefaultInstaller:

	def __init__(self, container: Container):
		self._container = container

	def install(self):
		self._install_db()
		self._install_repositories()
		self._install_services()

	def _install_db(self) -> None:
		database_url = os.getenv("DATABASE_URL")

		db_engine = create_db_engine(database_url)
		session_factory = create_session_factory(db_engine)
		self._container.db_session_factory.override(
			providers.Singleton(session_factory)
		)

	def _install_services(self):

		self._container.game_path_service.override(
			providers.Factory(
				GamePathService,
				game_data_path=self._container.config.game_data_path
			)
		)

		self._container.profile_service.override(
			providers.Factory(
				ProfileService,
				profile_repository=self._container.profile_repository
			)
		)

		self._container.scanner_service.override(
			providers.Factory(
				ScannerService,
				game_scanner=self._container.game_scanner,
				item_repository=self._container.item_repository,
				location_repository=self._container.location_repository,
				object_repository=self._container.object_repository
			)
		)

		self._container.item_tracking_service.override(
			providers.Factory(
				ItemTrackingService,
				item_repository=self._container.item_repository,
				location_repository=self._container.location_repository,
				object_repository=self._container.object_repository,
				object_has_item_repository=self._container.object_has_item_repository
			)
		)

	def _install_repositories(self):
		self._container.item_repository.override(
			providers.Singleton(
				ItemRepository,
				session=self._container.db_session_factory()
			)
		)

		self._container.location_repository.override(
			providers.Singleton(
				LocationRepository,
				session=self._container.db_session_factory()
			)
		)

		self._container.object_repository.override(
			providers.Singleton(
				ObjectRepository,
				session=self._container.db_session_factory()
			)
		)

		self._container.object_has_item_repository.override(
			providers.Singleton(
				ObjectHasItemRepository,
				session=self._container.db_session_factory()
			)
		)

		self._container.profile_repository.override(
			providers.Singleton(
				ProfilePostgresRepository,
				session=self._container.db_session_factory()
			)
		)
