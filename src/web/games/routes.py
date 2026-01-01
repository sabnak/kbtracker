import json
from collections.abc import Generator

from fastapi import APIRouter, Request, Form, Query, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide

from src.web.games.forms import GameCreateForm, ScanForm
from src.web.template_filters import register_filters
from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.IGameService import IGameService
from src.domain.game.services.ScannerService import ScannerService
from src.domain.game.services import ItemService
from src.domain.game.events.ScanEventType import ScanEventType
from src.domain.game.events.ScanProgressEvent import ScanProgressEvent
from src.domain.profile.IProfileService import IProfileService
from src.domain.exceptions import DuplicateEntityException, DatabaseOperationException, InvalidRegexException
from src.web.dependencies.game_context import get_game_context, GameContext
from src.domain.CrudRepository import _game_context


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
	game_path_service: IGamePathService = Depends(Provide["game_path_service"])
):
	"""
	Show game creation form
	"""
	available_paths = game_path_service.get_available_game_paths()
	return templates.TemplateResponse(
		"pages/game_create.html",
		{
			"request": request,
			"available_game_paths": available_paths
		}
	)


@router.post("/games/create")
@inject
async def create_game(
	name: str = Form(...),
	path: str = Form(...),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Create new game
	"""
	form_data = GameCreateForm(name=name, path=path)
	game_service.create_game(form_data.name, form_data.path)
	return RedirectResponse(url="/games", status_code=303)


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


@router.post("/games/{game_id}/scan")
@inject
async def scan_game_files(
	request: Request,
	game_id: int,
	language: str = Form(...),
	game_context: GameContext = Depends(get_game_context),
	scanner_service: ScannerService = Depends(Provide["scanner_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Execute game file scan
	"""
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	languages = [
		{"value": "rus", "label": "Russian"},
		{"value": "eng", "label": "English"},
		{"value": "ger", "label": "German"},
		{"value": "pol", "label": "Polish"}
	]

	try:
		form_data = ScanForm(language=language)

		result = scanner_service.scan_game_files(
			game_id=game_id,
			language=form_data.language.value
		)

		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"game": game,
				"languages": languages,
				"success": True,
				"result": result
			}
		)
	except DuplicateEntityException as e:
		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"game": game,
				"languages": languages,
				"error": (
					f"Data already exists: {e.message}. "
					f"This game may have already been scanned."
				)
			}
		)
	except DatabaseOperationException as e:
		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"game": game,
				"languages": languages,
				"error": f"Database error: {e.message}"
			}
		)
	except NotImplementedError as e:
		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"game": game,
				"languages": languages,
				"error": str(e)
			}
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
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		# Return error event immediately
		def error_stream() -> Generator[str, None, None]:
			event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error="Game not found",
				message=f"Game with ID {game_id} not found"
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
			for event in scanner_service.scan_game_files_stream(game_id, language):
				# Format as SSE: "data: {json}\n\n"
				event_data = json.dumps(event.to_dict())
				yield f"data: {event_data}\n\n"

		except DuplicateEntityException as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=f"Data already exists: {e.message}",
				message="This game may have already been scanned"
			)
			yield f"data: {json.dumps(error_event.to_dict())}\n\n"

		except DatabaseOperationException as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=f"Database error: {e.message}",
				message="Database operation failed"
			)
			yield f"data: {json.dumps(error_event.to_dict())}\n\n"

		except Exception as e:
			error_event = ScanProgressEvent(
				event_type=ScanEventType.SCAN_ERROR,
				error=str(e),
				message="Unexpected error during scan"
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
	propbit: str = Query(default=""),
	item_set_id_str: str = Query(default="", alias="item_set_id"),
	id_str: str = Query(default="", alias="id"),
	sort_by: str = Query(default="name"),
	sort_order: str = Query(default="asc"),
	game_context: GameContext = Depends(get_game_context),
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	List all items for a game with set information and advanced filters
	"""
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	# Convert string parameters to proper types
	level = int(level_str) if level_str else None
	item_set_id = int(item_set_id_str) if item_set_id_str else None
	item_id = int(id_str) if id_str.strip() else None

	# Normalize empty strings to None for optional filters
	name_query = query.strip() if query.strip() else None
	hint_query = hint_regex.strip() if hint_regex.strip() else None
	propbit_query = propbit.strip() if propbit.strip() else None

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
			propbit=propbit_query,
			item_set_id=item_set_id,
			item_id=item_id,
			sort_by=sort_field,
			sort_order=sort_direction
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
			"selected_propbit": propbit,
			"selected_set_id": item_set_id,
			"selected_id": id_str,
			# Sort state
			"sort_by": sort_field,
			"sort_order": sort_direction,
			# Dropdown options
			"available_levels": available_levels,
			"available_propbits": available_propbits,
			"available_sets": available_sets,
			# Error handling
			"error": error_message
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
	_game_context.set(game_context)

	profiles = profile_service.list_profiles()
	return [{"id": p.id, "name": p.name} for p in profiles]
