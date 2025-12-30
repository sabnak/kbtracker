from collections.abc import Generator

from dependency_injector.wiring import Provide, inject

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.IGameRepository import IGameRepository
from src.domain.game.IItemsAndSetsScannerService import IItemsAndSetsScannerService
from src.domain.game.ILocalizationScannerService import ILocalizationScannerService
from src.domain.game.IShopsAndLocationsScannerService import IShopsAndLocationsScannerService
from src.domain.game.events.ResourceType import ResourceType
from src.domain.game.events.ScanEventType import ScanEventType
from src.domain.game.events.ScanProgressEvent import ScanProgressEvent
from src.domain.game.dto.ScanResults import ScanResults


class ScannerService:

	@inject
	def __init__(
		self,
		game_repository: IGameRepository = Provide[Container.game_repository],
		localization_scanner_service: ILocalizationScannerService = Provide[Container.localization_scanner_service],
		items_and_sets_scanner_service: IItemsAndSetsScannerService = Provide[Container.items_and_sets_scanner_service],
		shops_and_locations_scanner_service: IShopsAndLocationsScannerService = Provide[Container.shops_and_locations_scanner_service],
		config: Config = Provide[Container.config]
	):
		self._game_repository = game_repository
		self._localization_scanner = localization_scanner_service
		self._items_and_sets_scanner = items_and_sets_scanner_service
		self._shops_and_locations_scanner = shops_and_locations_scanner_service
		self._config = config

	def scan_game_files(
		self,
		game_id: int,
		language: str
	) -> ScanResults:
		"""
		Scan game files and populate database

		:param game_id:
			Game ID to scan
		:param language:
			Language code (rus, eng, ger, pol)
		:return:
			ScanResults with counts of scanned items, locations, shops, and sets
		"""
		localizations_string = len(self._localization_scanner.scan(game_id, language))

		items, sets = self._items_and_sets_scanner.scan(game_id)
		total_items = len(items)
		total_sets = len(sets)

		locations, shops = self._shops_and_locations_scanner.scan(game_id, language)

		return ScanResults(
			items=total_items,
			locations=len(locations),
			shops=len(shops),
			sets=total_sets,
			localizations=localizations_string
		)

	def scan_game_files_stream(
		self,
		game_id: int,
		language: str
	) -> Generator[ScanProgressEvent, None, ScanResults]:
		"""
		Scan game files and yield progress events

		:param game_id:
			Game ID to scan
		:param language:
			Language code (rus, eng, ger, pol)
		:return:
			Generator yielding ScanProgressEvent instances, returns ScanResults
		"""
		try:
			# Emit scan started event
			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_STARTED,
				message=f"Starting scan for game {game_id} with language {language}"
			)

			# Step 1: Scan localizations
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.LOCALIZATIONS,
				message="Scanning localization files"
			)

			localizations = self._localization_scanner.scan(game_id, language)
			localizations_count = len(localizations)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.LOCALIZATIONS,
				count=localizations_count,
				message=f"Scanned {localizations_count} localizations"
			)

			# Step 2: Parse and create items/sets
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.ITEMS,
				message="Parsing items and sets"
			)

			items, sets = self._items_and_sets_scanner.scan(game_id)
			total_items = len(items)
			total_sets = len(sets)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.ITEMS,
				count=total_items,
				message=f"Created {total_items} items"
			)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.SETS,
				count=total_sets,
				message=f"Created {total_sets} item sets"
			)

			# Step 3: Parse and create locations/shops
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.LOCATIONS,
				message="Parsing locations and shops"
			)

			locations, shops = self._shops_and_locations_scanner.scan(game_id, language)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.LOCATIONS,
				count=len(locations),
				message=f"Created {len(locations)} locations"
			)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.SHOPS,
				count=len(shops),
				message=f"Created {len(shops)} shops"
			)

			# Final results
			results = ScanResults(
				items=total_items,
				locations=len(locations),
				shops=len(shops),
				sets=total_sets,
				localizations=localizations_count
			)

			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_COMPLETED,
				message="Scan completed successfully"
			)

			return results

		except Exception as e:
			# Emit error event
			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=str(e),
				message=f"Scan failed: {str(e)}"
			)
			raise
