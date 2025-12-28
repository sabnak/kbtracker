from dependency_injector import containers, providers

from src.domain.game.IGameScanner import IGameScanner
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IObjectHasItemRepository import IObjectHasItemRepository
from src.domain.game.IObjectRepository import IObjectRepository
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
	object_repository = providers.AbstractSingleton(IObjectRepository)
	object_has_item_repository = providers.AbstractSingleton(IObjectHasItemRepository)
	profile_repository = providers.AbstractSingleton(IProfileRepository)

	game_scanner = providers.AbstractSingleton(IGameScanner)

	profile_service = providers.AbstractFactory(IProfileService)
	scanner_service = providers.AbstractFactory(IGameScanner)
	item_tracking_service = providers.AbstractFactory()
