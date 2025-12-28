from src.domain.game.IGameScanner import IGameScanner
from src.domain.game.IItemRepository import IItemRepository
from src.domain.game.ILocationRepository import ILocationRepository
from src.domain.game.IObjectRepository import IObjectRepository


class ScannerService:

	def __init__(
		self,
		game_scanner: IGameScanner,
		item_repository: IItemRepository,
		location_repository: ILocationRepository,
		object_repository: IObjectRepository
	):
		self._game_scanner = game_scanner
		self._item_repository = item_repository
		self._location_repository = location_repository
		self._object_repository = object_repository

	def scan_game_files(
		self,
		game_version: str,
		language: str,
		game_data_path: str
	) -> dict[str, int]:
		"""
		Scan game files and populate database

		:param game_version:
			Game version (e.g., "darkside")
		:param language:
			Language code (ru, eng, ger, pol)
		:param game_data_path:
			Base path to game data
		:return:
			Dictionary with counts of scanned items and objects
		"""
		language_suffix = f"_{language}" if language != "ru" else ""
		file_path = f"{game_data_path}/{game_version}/loc_ses{language_suffix}.kfs"

		items = self._game_scanner.scan_items(file_path)
		self._item_repository.create_batch(items)

		objects_with_locations = self._game_scanner.scan_objects(file_path)

		unique_locations = {}
		for obj, loc in objects_with_locations:
			if loc.kb_id not in unique_locations:
				unique_locations[loc.kb_id] = loc

		created_locations = self._location_repository.create_batch(
			list(unique_locations.values())
		)

		location_map = {loc.kb_id: loc.id for loc in created_locations}

		objects_to_create = []
		for obj, loc in objects_with_locations:
			obj.location_id = location_map[loc.kb_id]
			objects_to_create.append(obj)

		self._object_repository.create_batch(objects_to_create)

		return {
			"items": len(items),
			"locations": len(created_locations),
			"objects": len(objects_to_create)
		}
