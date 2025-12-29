from dependency_injector import containers, providers

from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.profile.IProfileRepository import IProfileRepository
from src.domain.profile.IProfileService import IProfileService


class Container(containers.DeclarativeContainer):

	wiring_config = containers.WiringConfiguration(
		packages=["src.domain.profile", "src.web"]
	)

	config = providers.Configuration()

	db_session_factory = providers.AbstractSingleton()

	item_repository = providers.AbstractSingleton(IItemRepository)
	location_repository = providers.AbstractSingleton(ILocationRepository)
	shop_repository = providers.AbstractSingleton(IShopRepository)
	shop_has_item_repository = providers.AbstractSingleton(IShopHasItemRepository)
	profile_repository = providers.AbstractSingleton(IProfileRepository)

	game_path_service = providers.AbstractFactory(IGamePathService)
	profile_service = providers.AbstractFactory(IProfileService)
	scanner_service = providers.AbstractFactory()
	item_tracking_service = providers.AbstractFactory()
