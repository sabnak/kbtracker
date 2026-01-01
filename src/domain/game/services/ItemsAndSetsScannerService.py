import os

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.IItemSetRepository import IItemSetRepository
from src.domain.game.IItemsAndSetsScannerService import IItemsAndSetsScannerService
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
		config: Config = Provide[Container.config]
	):
		self._item_repository = item_repository
		self._item_set_repository = item_set_repository
		self._game_repository = game_repository
		self._parser = parser
		self._config = config

	def scan(self, game_id: int) -> tuple[list[Item], list[ItemSet]]:
		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		sessions_path = os.path.join(self._config.game_data_path, game.path, "sessions")
		parse_results = self._parser.parse(sessions_path)

		all_items = []
		all_sets = []

		for set_kb_id, set_data in parse_results.items():
			if set_kb_id == "setless":
				items = set_data["items"]
				created_items = self._item_repository.create_batch(items)
				all_items.extend(created_items)
			else:
				item_set = ItemSet(id=0, kb_id=set_kb_id)
				created_set = self._item_set_repository.create(item_set)
				all_sets.append(created_set)

				items = set_data["items"]
				for item in items:
					item.item_set_id = created_set.id
				created_items = self._item_repository.create_batch(items)
				all_items.extend(created_items)

		return all_items, all_sets
