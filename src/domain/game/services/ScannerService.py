from collections.abc import Generator
import traceback

from dependency_injector.wiring import Provide

from src.core.Config import Config
from src.core.Container import Container
from src.domain.game.interfaces.IAtomMapScannerService import IAtomMapScannerService
from src.domain.app.interfaces.IGameRepository import IGameRepository
from src.domain.game.interfaces.IItemsAndSetsScannerService import IItemsAndSetsScannerService
from src.domain.game.interfaces.ILocalizationScannerService import ILocalizationScannerService
from src.domain.game.interfaces.ISpellsScannerService import ISpellsScannerService
from src.domain.game.interfaces.IUnitsScannerService import IUnitsScannerService
from src.domain.game.dto.ScanResults import ScanResults
from src.domain.game.events.ResourceType import ResourceType
from src.domain.game.events.ScanEventType import ScanEventType
from src.domain.game.events.ScanProgressEvent import ScanProgressEvent
from src.utils.parsers.game_data.IKFSExtractor import IKFSExtractor


class ScannerService:

	def __init__(
		self,
		game_repository: IGameRepository = Provide[Container.game_repository],
		localization_scanner_service: ILocalizationScannerService = Provide[Container.localization_scanner_service],
		items_and_sets_scanner_service: IItemsAndSetsScannerService = Provide[Container.items_and_sets_scanner_service],
		spells_scanner_service: ISpellsScannerService = Provide[Container.spells_scanner_service],
		units_scanner_service: IUnitsScannerService = Provide[Container.units_scanner_service],
		atom_map_scanner_service: IAtomMapScannerService = Provide[Container.atom_map_scanner_service],
		kfs_extractor: IKFSExtractor = Provide[Container.kfs_extractor],
		config: Config = Provide[Container.config]
	):
		self._game_repository = game_repository
		self._localization_scanner = localization_scanner_service
		self._items_and_sets_scanner = items_and_sets_scanner_service
		self._spells_scanner = spells_scanner_service
		self._units_scanner = units_scanner_service
		self._atom_map_scanner = atom_map_scanner_service
		self._kfs_extractor = kfs_extractor
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
		from datetime import datetime

		game = self._game_repository.get_by_id(game_id)
		if not game:
			raise ValueError(f"Game with ID {game_id} not found")

		# Update last_scan_time at start of scan
		self._game_repository.update_last_scan_time(game_id, datetime.now())

		self._kfs_extractor.extract_archives(game)

		localizations_string = len(self._localization_scanner.scan(game_id, game.path, language))

		items, sets = self._items_and_sets_scanner.scan(game_id, game.path)
		total_items = len(items)
		total_sets = len(sets)

		units = self._units_scanner.scan(game_id, game.path)
		total_units = len(units)

		spells = self._spells_scanner.scan(game_id, game.path)
		total_spells = len(spells)

		atoms = self._atom_map_scanner.scan(game_id, game.path, language)

		return ScanResults(
			items=total_items,
			atoms=len(atoms),
			sets=total_sets,
			localizations=localizations_string,
			spells=total_spells,
			units=total_units
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
		from datetime import datetime

		try:
			# Emit scan started event
			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_STARTED,
				message=f"Starting scan for game {game_id} with language {language}"
			)

			# Get game info
			game = self._game_repository.get_by_id(game_id)
			if not game:
				raise ValueError(f"Game with ID {game_id} not found")

			# Update last_scan_time at start of scan
			self._game_repository.update_last_scan_time(game_id, datetime.now())

			# Extract archives ONCE
			yield ScanProgressEvent(
				event_type=ScanEventType.EXTRACTION_STARTED,
				message="Extracting game archives..."
			)

			self._kfs_extractor.extract_archives(game)

			yield ScanProgressEvent(
				event_type=ScanEventType.EXTRACTION_COMPLETED,
				message="Archive extraction complete"
			)

			# Step 1: Scan localizations
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.LOCALIZATIONS,
				message="Scanning localization files"
			)

			localizations = self._localization_scanner.scan(game_id, game.path, language)
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

			items, sets = self._items_and_sets_scanner.scan(game_id, game.path)
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

			# Step 3: Parse and create units
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.UNITS,
				message="Parsing units"
			)

			units = self._units_scanner.scan(game_id, game.path)
			total_units = len(units)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.UNITS,
				count=total_units,
				message=f"Created {total_units} units"
			)

			# Step 4: Parse and create spells
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.SPELLS,
				message="Parsing spells"
			)

			spells = self._spells_scanner.scan(game_id, game.path)
			total_spells = len(spells)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.SPELLS,
				count=total_spells,
				message=f"Created {total_spells} spells"
			)

			# Step 5: Parse and create atoms
			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_STARTED,
				resource_type=ResourceType.ATOMS,
				message="Parsing atoms"
			)

			atoms = self._atom_map_scanner.scan(game_id, game.path, language)

			yield ScanProgressEvent(
				event_type=ScanEventType.RESOURCE_COMPLETED,
				resource_type=ResourceType.ATOMS,
				count=len(atoms),
				message=f"Created {len(atoms)} atoms"
			)

			# Final results
			results = ScanResults(
				items=total_items,
				atoms=len(atoms),
				sets=total_sets,
				localizations=localizations_count,
				spells=total_spells,
				units=total_units
			)

			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_COMPLETED,
				message="Scan completed successfully"
			)

			return results

		except Exception as e:
			# Emit error event with structured error data
			yield ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=str(e),
				message="Scan failed during execution",
				error_type=type(e).__name__,
				error_traceback=traceback.format_exc()
			)
			raise
