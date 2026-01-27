import json
import traceback
from collections.abc import Generator

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Request, Form, Query, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from src.domain.exceptions import DuplicateEntityException, DatabaseOperationException, InvalidRegexException
from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.app.interfaces.IGameService import IGameService
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISpellRepository import ISpellRepository
from src.domain.game.interfaces.IUnitRepository import IUnitRepository
from src.domain.game.entities.UnitClass import UnitClass
from src.domain.game.entities.SpellSchool import SpellSchool
from src.domain.game.interfaces.IShopInventoryService import IShopInventoryService
from src.domain.game.interfaces.IHeroInventoryRepository import IHeroInventoryRepository
from src.domain.game.dto.ShopsGroupBy import ShopsGroupBy
from src.domain.game.dto.UnitFilterDto import UnitFilterDto
from src.domain.game.entities.ShopProductType import ShopProductType
from src.domain.game.entities.InventoryEntityType import InventoryEntityType
from src.domain.game.events.ScanEventType import ScanEventType
from src.domain.game.events.ScanProgressEvent import ScanProgressEvent
from src.domain.base.repositories.CrudRepository import GAME_CONTEXT
from src.domain.game.services.ItemService import ItemService
from src.domain.game.services.ScannerService import ScannerService
from src.web.dependencies.game_context import get_game_context, GameContext
from src.web.games.forms import GameCreateForm, ScanForm, SpellFilterForm, UnitFilterForm
from src.web.template_filters import register_filters

router = APIRouter(tags=["games"])
templates = Jinja2Templates(directory="src/web/templates")
register_filters(templates)


@router.get("/games", response_class=HTMLResponse)
@inject
async def list_games(
	request: Request,
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	List all games
	"""
	games = game_service.list_games()
	return templates.TemplateResponse(
		"pages/game_list.html",
		{"request": request, "games": games}
	)


@router.get("/games/create", response_class=HTMLResponse)
@inject
async def create_game_form(
	request: Request,
	game_path_service: IGamePathService = Depends(Provide["game_path_service"]),
	game_config_service = Depends(Provide["game_config_service"])
):
	"""
	Show game creation form
	"""
	available_paths = game_path_service.get_available_game_paths()
	supported_games = game_config_service.get_supported_games()

	# Convert to JSON-serializable format
	games_data = [
		{
			"name": game.name,
			"session": game.session,
			"saves_pattern": game.saves_pattern,
			"campaigns": [
				{"name": c.name, "session": c.session}
				for c in (game.campaigns or [])
			] if game.campaigns else []
		}
		for game in supported_games
	]

	return templates.TemplateResponse(
		"pages/game_create.html",
		{
			"request": request,
			"available_game_paths": available_paths,
			"supported_games": games_data
		}
	)


@router.post("/games/create")
@inject
async def create_game(
	request: Request,
	name: str = Form(...),
	path: str = Form(...),
	game_type: str = Form(...),
	campaign_name: str = Form(None),
	custom_campaign_session: str = Form(None),
	game_service: IGameService = Depends(Provide["game_service"]),
	game_config_service = Depends(Provide["game_config_service"]),
	game_path_service: IGamePathService = Depends(Provide["game_path_service"]),
	config = Depends(Provide["config"])
):
	"""
	Create new game with computed sessions and saves_pattern
	"""
	# Validate form data
	form_data = GameCreateForm(
		name=name,
		path=path,
		game_type=game_type,
		campaign_name=campaign_name,
		custom_campaign_session=custom_campaign_session
	)

	# Get game config
	game_config = game_config_service.get_game_config_by_name(form_data.game_type)

	if not game_config:
		# Return error - invalid game type
		available_paths = game_path_service.get_available_game_paths()
		supported_games = game_config_service.get_supported_games()
		games_data = [
			{
				"name": game.name,
				"session": game.session,
				"saves_pattern": game.saves_pattern,
				"campaigns": [
					{"name": c.name, "session": c.session}
					for c in (game.campaigns or [])
				] if game.campaigns else []
			}
			for game in supported_games
		]

		return templates.TemplateResponse(
			"pages/game_create.html",
			{
				"request": request,
				"available_game_paths": available_paths,
				"supported_games": games_data,
				"error": "Invalid game type selected"
			}
		)

	# Validate campaign selection for games with campaigns
	if game_config.campaigns and not form_data.campaign_name:
		# Return error - campaign is required for this game
		available_paths = game_path_service.get_available_game_paths()
		supported_games = game_config_service.get_supported_games()
		games_data = [
			{
				"name": game.name,
				"session": game.session,
				"saves_pattern": game.saves_pattern,
				"campaigns": [
					{"name": c.name, "session": c.session}
					for c in (game.campaigns or [])
				] if game.campaigns else []
			}
			for game in supported_games
		]

		return templates.TemplateResponse(
			"pages/game_create.html",
			{
				"request": request,
				"available_game_paths": available_paths,
				"supported_games": games_data,
				"error": "Campaign selection is required for this game"
			}
		)

	# Determine campaign session
	campaign_session = None
	if form_data.campaign_name:
		if form_data.campaign_name == "custom":
			campaign_session = form_data.custom_campaign_session

			if not campaign_session:
				# Return error - custom campaign requires session
				available_paths = game_path_service.get_available_game_paths()
				supported_games = game_config_service.get_supported_games()
				games_data = [
					{
						"name": game.name,
						"session": game.session,
						"saves_pattern": game.saves_pattern,
						"campaigns": [
							{"name": c.name, "session": c.session}
							for c in (game.campaigns or [])
						] if game.campaigns else []
					}
					for game in supported_games
				]

				return templates.TemplateResponse(
					"pages/game_create.html",
					{
						"request": request,
						"available_game_paths": available_paths,
						"supported_games": games_data,
						"error": "Custom campaign requires session name"
					}
				)

			# Validate session exists
			if not game_config_service.validate_campaign_session_exists(
				form_data.path,
				campaign_session,
				config.game_data_path
			):
				# Return error - session directory not found
				available_paths = game_path_service.get_available_game_paths()
				supported_games = game_config_service.get_supported_games()
				games_data = [
					{
						"name": game.name,
						"session": game.session,
						"saves_pattern": game.saves_pattern,
						"campaigns": [
							{"name": c.name, "session": c.session}
							for c in (game.campaigns or [])
						] if game.campaigns else []
					}
					for game in supported_games
				]

				return templates.TemplateResponse(
					"pages/game_create.html",
					{
						"request": request,
						"available_game_paths": available_paths,
						"supported_games": games_data,
						"error": f"Session directory not found: {campaign_session}"
					}
				)
		else:
			# Find predefined campaign
			if game_config.campaigns:
				for camp in game_config.campaigns:
					if camp.name == form_data.campaign_name:
						campaign_session = camp.session
						break

	# Compute values
	sessions = game_config_service.compute_sessions(game_config, campaign_session)
	saves_pattern = game_config_service.compute_saves_pattern(game_config, campaign_session)

	# Create game
	game_service.create_game(
		name=form_data.name,
		path=form_data.path,
		sessions=sessions,
		saves_pattern=saves_pattern
	)

	return RedirectResponse(url="/games", status_code=303)


@router.get("/api/games/scan-sessions")
@inject
async def scan_sessions(
	path: str = Query(...),
	config = Depends(Provide["config"])
):
	"""
	Scan sessions directory for available session folders

	:param path:
		Game path to scan
	:param config:
		Application config
	:return:
		JSON with list of session directories
	"""
	import os

	sessions_dir = os.path.join(config.game_data_path, path, "sessions")

	try:
		if not os.path.exists(sessions_dir):
			return {
				"sessions": [],
				"error": f"Sessions directory not found: {sessions_dir}"
			}

		entries = os.listdir(sessions_dir)
		sessions = [
			entry for entry in entries
			if os.path.isdir(os.path.join(sessions_dir, entry))
		]

		return {"sessions": sorted(sessions)}
	except (OSError, PermissionError) as e:
		return {
			"sessions": [],
			"error": f"Error accessing {sessions_dir}: {str(e)}"
		}


@router.post("/games/{game_id}/delete")
@inject
async def delete_game(
	game_id: int,
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Delete game (cascades to profiles and game data)
	"""
	game_service.delete_game(game_id)
	return RedirectResponse(url="/games", status_code=303)


@router.get("/games/{game_id}/scan", response_class=HTMLResponse)
@inject
async def scan_form(
	request: Request,
	game_id: int,
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Show game file scanner form
	"""
	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	languages = [
		{"value": "rus", "label": "Russian"},
		{"value": "eng", "label": "English"},
		{"value": "ger", "label": "German"},
		{"value": "pol", "label": "Polish"}
	]

	return templates.TemplateResponse(
		"pages/scan.html",
		{"request": request, "game": game, "languages": languages}
	)


@router.get("/games/{game_id}/scan/stream")
@inject
async def scan_game_files_stream(
	game_id: int,
	language: str = Query(...),
	game_context: GameContext = Depends(get_game_context),
	scanner_service: ScannerService = Depends(Provide["scanner_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Stream scan progress events using Server-Sent Events

	:param game_id:
		Game ID to scan
	:param language:
		Language code (rus, eng, ger, pol)
	:param game_context:
		Game context with schema information
	:param scanner_service:
		Scanner service dependency
	:param game_service:
		Game service dependency
	:return:
		StreamingResponse with text/event-stream content type
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		# Return error event immediately
		def error_stream() -> Generator[str, None, None]:
			event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error="Game not found",
				message=f"Game with ID {game_id} not found",
				error_type="ValidationError"
			)
			yield f"data: {json.dumps(event.to_dict())}\n\n"

		return StreamingResponse(
			error_stream(),
			media_type="text/event-stream"
		)

	def event_stream() -> Generator[str, None, None]:
		"""
		Generate SSE-formatted events

		:return:
			Generator yielding SSE formatted strings
		"""
		try:
			# Check if this is a rescan and prepare if needed
			if game.last_scan_time is not None:
				prep_event = ScanProgressEvent(
					event_type=ScanEventType.SCAN_STARTED,
					message="Preparing for rescan: clearing existing data..."
				)
				yield f"data: {json.dumps(prep_event.to_dict())}\n\n"

				game_service.prepare_rescan(game_id)

			# Proceed with normal scan
			for event in scanner_service.scan_game_files_stream(game_id, language):
				# Format as SSE: "data: {json}\n\n"
				event_data = json.dumps(event.to_dict())
				yield f"data: {event_data}\n\n"

		except DuplicateEntityException as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=f"Data already exists: {e.message}",
				message="This game may have already been scanned",
				error_type=type(e).__name__,
				error_traceback=traceback.format_exc()
			)
			yield f"data: {json.dumps(error_event.to_dict())}\n\n"

		except DatabaseOperationException as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=f"Database error: {e.message}",
				message="Database operation failed",
				error_type=type(e).__name__,
				error_traceback=traceback.format_exc()
			)
			yield f"data: {json.dumps(error_event.to_dict())}\n\n"

		except Exception as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=str(e),
				message="Unexpected error during scan",
				error_type=type(e).__name__,
				error_traceback=traceback.format_exc()
			)
			yield f"data: {json.dumps(error_event.to_dict())}\n\n"

	return StreamingResponse(
		event_stream(),
		media_type="text/event-stream",
		headers={
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"X-Accel-Buffering": "no"
		}
	)


@router.get("/games/{game_id}/items", response_class=HTMLResponse)
@inject
async def list_items(
	request: Request,
	game_id: int,
	query: str = Query(default=""),
	level_str: str = Query(default="", alias="level"),
	hint_regex: str = Query(default=""),
	propbits: list[str] = Query(default=[], alias="propbit"),
	item_set_id_str: str = Query(default="", alias="item_set_id"),
	id_str: str = Query(default="", alias="id"),
	sort_by: str = Query(default="name"),
	sort_order: str = Query(default="asc"),
	profile_id: int | None = Query(default=None),
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemService = Depends(Provide["item_service"]),
	game_service: IGameService = Depends(Provide["game_service"]),
	profile_repository: IProfileRepository = Depends(Provide["profile_repository"]),
	shop_inventory_service: IShopInventoryService = Depends(Provide["shop_inventory_service"]),
	hero_inventory_repository: IHeroInventoryRepository = Depends(Provide["hero_inventory_repository"])
):
	"""
	List all items for a game with set information and advanced filters
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	# Fetch profiles for filter dropdown
	profiles = profile_repository.list_all()

	# Determine selected profile (default to "All Profiles")
	# profile_id = None or 0 means "All Profiles" (no filter)
	selected_profile_id = None
	if profiles and profile_id is not None and profile_id != 0:
		selected_profile = next((p for p in profiles if p.id == profile_id), None)
		if selected_profile:
			selected_profile_id = profile_id
		else:
			return RedirectResponse(url=f"/games/{game_id}/items", status_code=303)

	# Fetch shop data for items (only when profile selected)
	shops_by_item = {}
	if selected_profile_id:
		shops_by_item = shop_inventory_service.get_shops(
			profile_id=selected_profile_id,
			group_by=ShopsGroupBy.ITEM,
			types=(ShopProductType.ITEM,)
		)

	# Fetch hero inventory for items (only when profile selected)
	hero_items_set = set()
	hero_items_dict = {}
	if selected_profile_id:
		hero_inventory = hero_inventory_repository.get_by_profile(
			profile_id=selected_profile_id,
			product_types=[InventoryEntityType.ITEM]
		)
		hero_items_set = {inv.product_id for inv in hero_inventory}
		hero_items_dict = {inv.product_id: inv for inv in hero_inventory}

	# Convert string parameters to proper types
	level = int(level_str) if level_str else None
	item_set_id = int(item_set_id_str) if item_set_id_str else None
	item_id = int(id_str) if id_str.strip() else None

	# Normalize empty strings to None for optional filters
	name_query = query.strip() if query.strip() else None
	hint_query = hint_regex.strip() if hint_regex.strip() else None
	propbits_query = [pb.strip() for pb in propbits if pb.strip()] if propbits else None

	# Validate sort parameters
	allowed_sort_fields = ["name", "price", "level"]
	sort_field = sort_by if sort_by in allowed_sort_fields else "name"

	allowed_sort_orders = ["asc", "desc"]
	sort_direction = sort_order.lower() if sort_order.lower() in allowed_sort_orders else "asc"

	# Fetch dropdown options
	available_levels = item_tracking_service.get_available_levels()
	available_propbits = item_tracking_service.get_available_propbits()
	available_sets = item_tracking_service.get_available_item_sets()

	# Apply filters
	error_message = None
	try:
		items_with_sets = item_tracking_service.get_items_with_sets(
			name_query=name_query,
			level=level,
			hint_regex=hint_query,
			propbits=propbits_query,
			item_set_id=item_set_id,
			item_id=item_id,
			sort_by=sort_field,
			sort_order=sort_direction,
			profile_id=selected_profile_id
		)
	except InvalidRegexException as e:
		error_message = f"Invalid regex pattern: {e.message}"
		items_with_sets = []

	return templates.TemplateResponse(
		"pages/item_list.html",
		{
			"request": request,
			"game": game,
			"items_with_sets": items_with_sets,
			# Preserve filter values
			"query": query,
			"selected_level": level,
			"hint_regex": hint_regex,
			"selected_propbits": propbits,
			"selected_set_id": item_set_id,
			"selected_id": id_str,
			# Sort state
			"sort_by": sort_field,
			"sort_order": sort_direction,
			# Dropdown options
			"available_levels": available_levels,
			"available_propbits": available_propbits,
			"available_sets": available_sets,
			# Profile filter
			"profiles": profiles,
			"selected_profile_id": selected_profile_id,
			# Shop data
			"shops_by_item": shops_by_item,
			# Hero inventory data
			"hero_items_set": hero_items_set,
			"hero_items_dict": hero_items_dict,
			# Error handling
			"error": error_message
		}
	)


@router.get("/games/{game_id}/units", response_class=HTMLResponse)
@inject
async def list_units(
	request: Request,
	game_id: int,
	sort_by: str = Query(default="name"),
	sort_order: str = Query(default="asc"),
	filters: UnitFilterForm = Depends(),
	game_context: GameContext = Depends(get_game_context),
	unit_repository: IUnitRepository = Depends(Provide["unit_repository"]),
	game_service: IGameService = Depends(Provide["game_service"]),
	profile_repository: IProfileRepository = Depends(Provide["profile_repository"]),
	shop_inventory_service: IShopInventoryService = Depends(Provide["shop_inventory_service"])
):
	"""
	List all chesspiece units for a game with optional profile and cost filters
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	# Fetch profiles
	profiles = profile_repository.list_all()

	# Validate profile_id
	selected_profile_id = None
	if filters.profile_id:
		selected_profile = next((p for p in profiles if p.id == filters.profile_id), None)
		if selected_profile:
			selected_profile_id = filters.profile_id
		else:
			return RedirectResponse(url=f"/games/{game_id}/units", status_code=303)

	# Validate sort parameters
	allowed_sort_fields = ["name", "level", "race", "cost", "leadership", "attack", "defense", "speed", "initiative"]
	sort_field = sort_by if sort_by in allowed_sort_fields else "name"

	allowed_sort_orders = ["asc", "desc"]
	sort_direction = sort_order.lower() if sort_order.lower() in allowed_sort_orders else "asc"

	# Convert form to DTO
	filter_dto = UnitFilterDto(
		profile_id=selected_profile_id,
		min_cost=filters.min_cost,
		max_cost=filters.max_cost,
		min_attack=filters.min_attack,
		min_krit=filters.min_krit,
		min_hitpoint=filters.min_hitpoint,
		min_defense=filters.min_defense,
		min_speed=filters.min_speed,
		min_initiative=filters.min_initiative,
		min_resistance_fire=filters.min_resistance_fire,
		min_resistance_magic=filters.min_resistance_magic,
		min_resistance_poison=filters.min_resistance_poison,
		min_resistance_glacial=filters.min_resistance_glacial,
		min_resistance_physical=filters.min_resistance_physical,
		min_resistance_astral=filters.min_resistance_astral,
		level=filters.level
	)

	# Fetch units with filters
	units = unit_repository.search_with_filters(
		filters=filter_dto,
		unit_class=UnitClass.CHESSPIECE,
		sort_by=sort_field,
		sort_order=sort_direction
	)

	# Fetch shop data (only when profile selected)
	shops_for_sale = {}
	shops_garrison = {}
	if selected_profile_id:
		shops_for_sale = shop_inventory_service.get_shops(
			profile_id=selected_profile_id,
			group_by=ShopsGroupBy.UNIT,
			types=(ShopProductType.UNIT,)
		)
		shops_garrison = shop_inventory_service.get_shops(
			profile_id=selected_profile_id,
			group_by=ShopsGroupBy.UNIT,
			types=(ShopProductType.GARRISON,)
		)

	return templates.TemplateResponse(
		"pages/unit_list.html",
		{
			"request": request,
			"game": game,
			"units": units,
			"sort_by": sort_field,
			"sort_order": sort_direction,
			"profiles": profiles,
			"selected_profile_id": selected_profile_id,
			"shops_for_sale": shops_for_sale,
			"shops_garrison": shops_garrison,
			"filters": filters
		}
	)


@router.get("/games/{game_id}/spells", response_class=HTMLResponse)
@inject
async def list_spells(
	request: Request,
	game_id: int,
	filters: SpellFilterForm = Depends(),
	game_context: GameContext = Depends(get_game_context),
	spell_repository: ISpellRepository = Depends(Provide["spell_repository"]),
	game_service: IGameService = Depends(Provide["game_service"]),
	profile_repository: IProfileRepository = Depends(Provide["profile_repository"]),
	shop_inventory_service: IShopInventoryService = Depends(Provide["shop_inventory_service"])
):
	"""
	List all spells for a game (excluding hidden spells)
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	# Fetch profiles for filter dropdown
	profiles = profile_repository.list_all()

	# Determine selected profile (default to "All Profiles")
	# profile_id = None or 0 means "All Profiles" (no filter)
	selected_profile_id = None
	if profiles and filters.profile_id is not None and filters.profile_id != 0:
		selected_profile = next((p for p in profiles if p.id == filters.profile_id), None)
		if selected_profile:
			selected_profile_id = filters.profile_id
		else:
			return RedirectResponse(url=f"/games/{game_id}/spells", status_code=303)

	# Parse school filter
	selected_school = None
	if filters.school:
		try:
			selected_school = SpellSchool[filters.school.upper()]
		except KeyError:
			pass

	# Fetch spells with filters
	all_spells = spell_repository.search_with_filters(
		school=selected_school,
		profit=filters.profit,
		sort_by=filters.sort_by,
		sort_order=filters.sort_order,
		profile_id=selected_profile_id
	)

	# Filter hidden spells
	spells = [spell for spell in all_spells if spell.hide == 0]

	# Fetch shop data for spells (only when profile selected)
	shops_by_spell = {}
	if selected_profile_id:
		shops_by_spell = shop_inventory_service.get_shops(
			profile_id=selected_profile_id,
			group_by=ShopsGroupBy.SPELL,
			types=(ShopProductType.SPELL,)
		)

	return templates.TemplateResponse(
		"pages/spells.html",
		{
			"request": request,
			"game": game,
			"spells": spells,
			"sort_by": filters.sort_by,
			"sort_order": filters.sort_order,
			"profiles": profiles,
			"selected_profile_id": selected_profile_id,
			"shops_by_spell": shops_by_spell,
			"all_schools": list(SpellSchool),
			"selected_school": selected_school,
			"selected_profit": filters.profit
		}
	)


@router.get("/games/{game_id}/shops", response_class=HTMLResponse)
@inject
async def list_shops(
	request: Request,
	game_id: int,
	profile_id: int | None = Query(default=None),
	game_context: GameContext = Depends(get_game_context),
	shop_inventory_service: IShopInventoryService = Depends(Provide["shop_inventory_service"]),
	profile_repository: IProfileRepository = Depends(Provide["profile_repository"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	List all shops grouped by location for a game with profile filter
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	profiles = profile_repository.list_all()

	if profile_id is None:
		if not profiles:
			return templates.TemplateResponse(
				"pages/shop_list.html",
				{
					"request": request,
					"game": game,
					"profiles": [],
					"selected_profile_id": None,
					"locations": {}
				}
			)
		selected_profile_id = profiles[0].id
	else:
		selected_profile = next((p for p in profiles if p.id == profile_id), None)
		if not selected_profile:
			return RedirectResponse(url=f"/games/{game_id}/shops", status_code=303)
		selected_profile_id = profile_id

	locations = shop_inventory_service.get_shops(selected_profile_id)

	return templates.TemplateResponse(
		"pages/shop_list.html",
		{
			"request": request,
			"game": game,
			"profiles": profiles,
			"selected_profile_id": selected_profile_id,
			"locations": locations
		}
	)


@router.get("/api/games/{game_id}/profiles")
@inject
async def get_profiles_by_game(
	game_id: int,
	game_context: GameContext = Depends(get_game_context),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Get all profiles for a specific game

	:param game_id:
		The game ID to filter profiles by
	:param game_context:
		Game context with schema information
	:param profile_service:
		Profile service dependency
	:return:
		List of profile objects with id and name
	"""
	GAME_CONTEXT.set(game_context)

	profiles = profile_service.list_profiles()
	return [{"id": p.id, "name": p.name} for p in profiles]
