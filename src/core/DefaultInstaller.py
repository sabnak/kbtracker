import os

from dependency_injector import providers
from sqlalchemy.orm import sessionmaker

from src.core.Container import Container
from src.domain.filesystem.services.GamePathService import GamePathService
from src.domain.game.repositories.GameRepository import GameRepository
from src.domain.game.repositories.ItemRepository import ItemRepository
from src.domain.game.repositories.ItemSetRepository import ItemSetRepository
from src.domain.game.repositories.LocalizationRepository import LocalizationRepository
from src.domain.game.repositories.LocationRepository import LocationRepository
from src.domain.game.repositories.ShopHasItemRepository import ShopHasItemRepository
from src.domain.game.repositories.ShopRepository import ShopRepository
from src.domain.game.services.GameService import GameService
from src.domain.game.services.ItemTrackingService import ItemTrackingService
from src.domain.game.services.ScannerService import ScannerService
from src.domain.profile.repositories.ProfilePostgresRepository import ProfilePostgresRepository
from src.domain.profile.services.ProfileService import ProfileService
from src.utils.db import create_db_engine


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
		self._container.db_session_factory.override(
			providers.Factory(sessionmaker, autocommit=False, autoflush=False, bind=db_engine)
		)

	def _install_services(self):

		self._container.game_path_service.override(
			providers.Factory(
				GamePathService,
				game_data_path=self._container.config.game_data_path
			)
		)

		self._container.game_service.override(
			providers.Factory(
				GameService,
				game_repository=self._container.game_repository
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
				game_repository=self._container.game_repository,
				item_repository=self._container.item_repository,
				item_set_repository=self._container.item_set_repository,
				location_repository=self._container.location_repository,
				shop_repository=self._container.shop_repository
			)
		)

		self._container.item_tracking_service.override(
			providers.Factory(
				ItemTrackingService,
				item_repository=self._container.item_repository,
				location_repository=self._container.location_repository,
				shop_repository=self._container.shop_repository,
				shop_has_item_repository=self._container.shop_has_item_repository,
				item_set_repository=self._container.item_set_repository
			)
		)

	def _install_repositories(self):
		self._container.game_repository.override(
			providers.Singleton(GameRepository)
		)

		self._container.item_repository.override(
			providers.Singleton(ItemRepository)
		)

		self._container.item_set_repository.override(
			providers.Singleton(ItemSetRepository)
		)

		self._container.localization_repository.override(
			providers.Singleton(LocalizationRepository)
		)

		self._container.location_repository.override(
			providers.Singleton(LocationRepository)
		)

		self._container.shop_repository.override(
			providers.Singleton(ShopRepository)
		)

		self._container.shop_has_item_repository.override(
			providers.Singleton(ShopHasItemRepository)
		)

		self._container.profile_repository.override(
			providers.Singleton(ProfilePostgresRepository)
		)
