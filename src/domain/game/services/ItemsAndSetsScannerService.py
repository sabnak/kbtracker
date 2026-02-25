from logging import Logger

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.game.interfaces.IItemRepository import IItemRepository
from src.domain.game.interfaces.IItemSetRepository import IItemSetRepository
from src.domain.game.interfaces.IItemsAndSetsScannerService import IItemsAndSetsScannerService
from src.domain.game.entities.Item import Item
from src.domain.game.entities.ItemSet import ItemSet
from src.utils.parsers.game_data import IKFSItemsParser


class ItemsAndSetsScannerService(IItemsAndSetsScannerService):

	def __init__(
		self,
		item_repository: IItemRepository = Provide[Container.item_repository],
		item_set_repository: IItemSetRepository = Provide[Container.item_set_repository],
		game_repository: IGameRepository = Provide[Container.game_repository],
		parser: IKFSItemsParser = Provide[Container.kfs_items_parser],
		config: Config = Provide[Container.config],
		logger: Logger = Provide[Container.logger]
	):
		self._item_repository = item_repository
		self._item_set_repository = item_set_repository
		self._game_repository = game_repository
		self._parser = parser
		self._config = config
		self._logger = logger

	def scan(self, game_id: int) -> tuple[list[Item], list[ItemSet]]:
		parse_results = self._parser.parse(game_id)

		all_items = []
		all_sets = []

		for set_kb_id, items in parse_results.items():
			if set_kb_id == "setless":
				created_items = self._item_repository.create_batch(items)
				all_items.extend(created_items)
			else:
				item_set = ItemSet(id=0, kb_id=set_kb_id)
				self._logger.debug(f"Saving item set: {item_set}")
				created_set = self._item_set_repository.create(item_set)
				all_sets.append(created_set)

				for item in items:
					try:
						item.item_set_id = created_set.id
					except Exception:
						self._logger.error(f"Error while setting item set id: {item_set}")
						raise
				created_items = self._item_repository.create_batch(items)
				all_items.extend(created_items)

		return all_items, all_sets
