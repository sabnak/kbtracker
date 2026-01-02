from dependency_injector import containers, providers

from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IGameService import IGameService
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.ILocalizationRepository import ILocalizationRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.ISchemaManagementService import ISchemaManagementService
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.game.IProfileRepository import IProfileRepository
from src.domain.game.IProfileService import IProfileService
from src.domain.game.IUnitRepository import IUnitRepository


class Container(containers.DeclarativeContainer):

	wiring_config = containers.WiringConfiguration(
		packages=["src.domain.game", "src.web", "src.utils"]
	)

	config = providers.AbstractSingleton()

	db_session_factory = providers.AbstractFactory()

	game_repository = providers.AbstractSingleton(IGameRepository)
	item_repository = providers.AbstractSingleton(IItemRepository)
	item_set_repository = providers.AbstractSingleton(IItemSetRepository)
	localization_repository = providers.AbstractSingleton(ILocalizationRepository)
	location_repository = providers.AbstractSingleton(ILocationRepository)
	shop_repository = providers.AbstractSingleton(IShopRepository)
	shop_has_item_repository = providers.AbstractSingleton(IShopHasItemRepository)
	profile_repository = providers.AbstractSingleton(IProfileRepository)
	unit_repository = providers.AbstractSingleton(IUnitRepository)

	game_path_service = providers.AbstractFactory(IGamePathService)
	game_service = providers.AbstractFactory(IGameService)
	profile_service = providers.AbstractFactory(IProfileService)
	scanner_service = providers.AbstractFactory()
	item_service = providers.AbstractFactory()
	localization_scanner_service = providers.AbstractFactory()
	items_and_sets_scanner_service = providers.AbstractFactory()
	units_scanner_service = providers.AbstractFactory()
	locations_and_shops_scanner_service = providers.AbstractFactory()
	schema_management_service = providers.AbstractFactory(ISchemaManagementService)

	# Data extractors and parsers
	kfs_extractor = providers.AbstractSingleton()
	kfs_reader = providers.AbstractSingleton()
	kfs_items_parser = providers.AbstractSingleton()
	kfs_localization_parser = providers.AbstractSingleton()
	kfs_unit_parser = providers.AbstractSingleton()
	kfs_locations_and_shops_parser = providers.AbstractSingleton()

	# Factories
	unit_factory = providers.AbstractSingleton()

	# Save file parsers
	save_file_decompressor = providers.AbstractSingleton()
	shop_inventory_parser = providers.AbstractSingleton()
	campaign_identifier_parser = providers.AbstractSingleton()
