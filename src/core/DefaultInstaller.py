import os

from dependency_injector import providers
from sqlalchemy.orm import sessionmaker

from src.core.Config import Config
from src.core.Container import Container
from src.core.logging_config import setup_logging
from src.domain.filesystem.services.GamePathService import GamePathService
from src.domain.game.services.ProfileGameDataSyncerService import ProfileGameDataSyncerService
from src.utils.parsers.game_data.KFSExtractor import KFSExtractor
from src.utils.parsers.game_data.KFSReader import KFSReader
from src.utils.parsers.game_data.KFSItemsParser import KFSItemsParser
from src.utils.parsers.game_data.KFSLocalizationParser import KFSLocalizationParser
from src.utils.parsers.game_data.KFSSpellsParser import KFSSpellsParser
from src.utils.parsers.game_data.KFSUnitParser import KFSUnitParser
from src.utils.parsers.game_data.KFSAtomsMapInfoParser import KFSAtomsMapInfoParser
from src.domain.app.repositories.GameRepository import GameRepository
from src.domain.game.repositories.AtomMapRepository import AtomMapRepository
from src.domain.game.repositories.ItemRepository import ItemRepository
from src.domain.game.repositories.ItemSetRepository import ItemSetRepository
from src.domain.game.repositories.LocalizationRepository import LocalizationRepository
from src.domain.game.repositories.ShopInventoryRepository import ShopInventoryRepository
from src.domain.game.repositories.UnitRepository import UnitRepository
from src.domain.game.repositories.SpellRepository import SpellRepository
from src.domain.game.factories.LocFactory import LocFactory
from src.domain.game.factories.SpellFactory import SpellFactory
from src.domain.game.factories.UnitFactory import UnitFactory
from src.domain.game.services.AtomMapScannerService import AtomMapScannerService
from src.domain.app.services.GameService import GameService
from src.domain.game.services.ItemsAndSetsScannerService import ItemsAndSetsScannerService
from src.domain.game.services.ItemService import ItemService
from src.domain.game.services.ShopInventoryService import ShopInventoryService
from src.domain.game.services.LocalizationScannerService import LocalizationScannerService
from src.domain.game.services.ScannerService import ScannerService
from src.domain.game.services.SchemaManagementService import SchemaManagementService
from src.domain.game.services.SpellsScannerService import SpellsScannerService
from src.domain.game.services.UnitsScannerService import UnitsScannerService
from src.domain.game.repositories.ProfilePostgresRepository import ProfilePostgresRepository
from src.domain.game.services.ProfileService import ProfileService
from src.domain.game.services.SaveFileService import SaveFileService
from src.utils.db import create_db_engine
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.ShopInventoryParser import ShopInventoryParser
from src.utils.parsers.save_data.HeroSaveParser import HeroSaveParser


class DefaultInstaller:

	def __init__(self, container: Container):
		self._container = container

	def install(self):
		self._container.logger.override(providers.Singleton(setup_logging))
		self._container.config.override(providers.Singleton(Config))
		self._install_db()
		self._install_repositories()
		self._install_game_resource_processors()
		self._install_save_file_parsers()
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
				game_data_path=self._container.config().game_data_path
			)
		)

		self._container.game_service.override(providers.Factory(GameService))
		self._container.profile_service.override(providers.Factory(ProfileService))
		self._container.profile_data_syncer_service.override(providers.Factory(ProfileGameDataSyncerService))
		self._container.save_file_service.override(providers.Factory(SaveFileService))
		self._container.scanner_service.override(providers.Factory(ScannerService))
		self._container.item_service.override(providers.Factory(ItemService))
		self._container.shop_inventory_service.override(providers.Factory(ShopInventoryService))
		self._container.localization_scanner_service.override(providers.Factory(LocalizationScannerService))
		self._container.items_and_sets_scanner_service.override(providers.Factory(ItemsAndSetsScannerService))
		self._container.spells_scanner_service.override(providers.Factory(SpellsScannerService))
		self._container.units_scanner_service.override(providers.Factory(UnitsScannerService))
		self._container.atom_map_scanner_service.override(providers.Factory(AtomMapScannerService))
		self._container.schema_management_service.override(providers.Factory(SchemaManagementService))

	def _install_game_resource_processors(self):
		self._container.kfs_extractor.override(providers.Singleton(KFSExtractor))
		self._container.kfs_reader.override(providers.Singleton(KFSReader))
		self._container.kfs_localization_parser.override(providers.Singleton(KFSLocalizationParser))
		self._container.kfs_items_parser.override(providers.Singleton(KFSItemsParser))
		self._container.kfs_unit_parser.override(providers.Singleton(KFSUnitParser))
		self._container.kfs_atoms_map_info_parser.override(providers.Singleton(KFSAtomsMapInfoParser))
		self._container.kfs_spells_parser.override(providers.Singleton(KFSSpellsParser))
		self._container.loc_factory.override(providers.Singleton(LocFactory))
		self._container.spell_factory.override(providers.Singleton(SpellFactory))
		self._container.unit_factory.override(providers.Singleton(UnitFactory))

	def _install_save_file_parsers(self):
		self._container.save_file_decompressor.override(providers.Singleton(SaveFileDecompressor))
		self._container.shop_inventory_parser.override(providers.Singleton(ShopInventoryParser))
		self._container.hero_save_parser.override(providers.Singleton(HeroSaveParser))

	def _install_repositories(self):
		self._container.game_repository.override(providers.Singleton(GameRepository))
		self._container.item_repository.override(providers.Singleton(ItemRepository))
		self._container.item_set_repository.override(providers.Singleton(ItemSetRepository))
		self._container.localization_repository.override(providers.Singleton(LocalizationRepository))
		self._container.atom_map_repository.override(providers.Singleton(AtomMapRepository))
		self._container.shop_inventory_repository.override(providers.Singleton(ShopInventoryRepository))
		self._container.profile_repository.override(providers.Singleton(ProfilePostgresRepository))
		self._container.spell_repository.override(providers.Singleton(SpellRepository))
		self._container.unit_repository.override(providers.Singleton(UnitRepository))
