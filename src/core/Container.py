from dependency_injector import containers, providers

from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IGameService import IGameService
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IShopHasItemRepository import IShopHasItemRepository
from src.domain.game.IShopRepository import IShopRepository
from src.domain.profile.IProfileRepository import IProfileRepository
from src.domain.profile.IProfileService import IProfileService


class Container(containers.DeclarativeContainer):

	wiring_config = containers.WiringConfiguration(
		packages=["src.domain.profile", "src.domain.game", "src.web"]
	)

	config = providers.Configuration()

	db_session_factory = providers.AbstractFactory()

	game_repository = providers.AbstractSingleton(IGameRepository)
	item_repository = providers.AbstractSingleton(IItemRepository)
	item_set_repository = providers.AbstractSingleton(IItemSetRepository)
	location_repository = providers.AbstractSingleton(ILocationRepository)
	shop_repository = providers.AbstractSingleton(IShopRepository)
	shop_has_item_repository = providers.AbstractSingleton(IShopHasItemRepository)
	profile_repository = providers.AbstractSingleton(IProfileRepository)

	game_path_service = providers.AbstractFactory(IGamePathService)
	game_service = providers.AbstractFactory(IGameService)
	profile_service = providers.AbstractFactory(IProfileService)
	scanner_service = providers.AbstractFactory()
	item_tracking_service = providers.AbstractFactory()
