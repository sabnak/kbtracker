from dependency_injector import containers, providers

from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.interfaces.IEntityRepository import IEntityRepository
from src.domain.app.interfaces.IGameConfigService import IGameConfigService
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.app.interfaces.IGameService import IGameService
from src.domain.app.interfaces.IMetaRepository import IMetaRepository
from src.domain.app.interfaces.ISettingsService import ISettingsService
from src.domain.app.interfaces.ITranslationService import ITranslationService
from src.domain.game.interfaces.IItemRepository import IItemRepository
from src.domain.game.interfaces.IItemSetRepository import IItemSetRepository
from src.domain.game.interfaces.IShopFactory import IShopFactory
from src.domain.game.interfaces.ILocalizationRepository import ILocalizationRepository
from src.domain.game.interfaces.IProfileGameDataSyncerService import IProfileGameDataSyncerService
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.domain.app.interfaces.ISchemaManagementService import ISchemaManagementService
from src.domain.game.interfaces.IShopInventoryRepository import IShopInventoryRepository
from src.domain.game.interfaces.ISpellRepository import ISpellRepository
from src.domain.game.interfaces.IUnitRepository import IUnitRepository


class Container(containers.DeclarativeContainer):

	wiring_config = containers.WiringConfiguration(
		packages=[
			"src.domain",
			"src.web",
			"src.utils",
			"src.tools"
		]
	)

	config = providers.AbstractSingleton()

	db_session_factory = providers.AbstractFactory()

	game_repository = providers.AbstractSingleton(IGameRepository)
	meta_repository = providers.AbstractSingleton(IMetaRepository)
	item_repository = providers.AbstractSingleton(IItemRepository)
	item_set_repository = providers.AbstractSingleton(IItemSetRepository)
	atom_map_repository = providers.AbstractSingleton(IEntityRepository)
	localization_repository = providers.AbstractSingleton(ILocalizationRepository)
	shop_inventory_repository = providers.AbstractSingleton(IShopInventoryRepository)
	profile_repository = providers.AbstractSingleton(IProfileRepository)
	spell_repository = providers.AbstractSingleton(ISpellRepository)
	unit_repository = providers.AbstractSingleton(IUnitRepository)

	# Services
	game_path_service = providers.AbstractFactory(IGamePathService)
	game_config_service = providers.AbstractFactory(IGameConfigService)
	game_service = providers.AbstractFactory(IGameService)
	settings_service = providers.AbstractFactory(ISettingsService)
	translation_service = providers.AbstractFactory(ITranslationService)
	profile_service = providers.AbstractFactory(IProfileService)
	profile_data_syncer_service = providers.AbstractFactory(IProfileGameDataSyncerService)
	save_file_service = providers.AbstractFactory(ISaveFileService)
	scanner_service = providers.AbstractFactory()
	item_service = providers.AbstractFactory()
	shop_inventory_service = providers.AbstractFactory()
	localization_scanner_service = providers.AbstractFactory()
	items_and_sets_scanner_service = providers.AbstractFactory()
	spells_scanner_service = providers.AbstractFactory()
	units_scanner_service = providers.AbstractFactory()
	atom_map_scanner_service = providers.AbstractFactory()
	schema_management_service = providers.AbstractFactory(ISchemaManagementService)

	# Data extractors and parsers
	kfs_extractor = providers.AbstractSingleton()
	kfs_reader = providers.AbstractSingleton()
	kfs_items_parser = providers.AbstractSingleton()
	kfs_localization_parser = providers.AbstractSingleton()
	kfs_spells_parser = providers.AbstractSingleton()
	kfs_unit_parser = providers.AbstractSingleton()

	# Factories
	loc_factory = providers.AbstractSingleton()
	spell_factory = providers.AbstractSingleton()
	unit_factory = providers.AbstractSingleton()
	shop_factory = providers.AbstractFactory(IShopFactory)

	# Save file parsers
	save_file_decompressor = providers.AbstractSingleton()
	shop_inventory_parser = providers.AbstractSingleton()
	hero_save_parser = providers.AbstractSingleton()

	logger = providers.AbstractSingleton()
