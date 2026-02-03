from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.domain.app.interfaces.IGameService import IGameService
from src.domain.base.repositories.CrudRepository import GAME_CONTEXT
from src.domain.exceptions import InvalidKbIdException
from src.domain.game.interfaces.IProfileRepository import IProfileRepository
from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.web.dependencies.game_context import get_game_context, GameContext

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/games/{game_id}/save-directories")
@inject
async def list_save_directories(
	game_id: int,
	game_context: GameContext = Depends(get_game_context),
	save_file_service: ISaveFileService = Depends(Provide["save_file_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	List available save directories for a game

	:param game_id:
		Game ID
	:param game_context:
		Game context
	:param save_file_service:
		Save file service
	:param game_service:
		Game service
	:return:
		Save directories grouped by game name
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	try:
		save_dirs = save_file_service.list_save_directories(game, limit=100)
		return save_dirs
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to list saves: {str(e)}")


@router.post("/games/{game_id}/scan-hero")
@inject
async def scan_hero(
	game_id: int,
	request_data: dict,
	game_context: GameContext = Depends(get_game_context),
	save_file_service: ISaveFileService = Depends(Provide["save_file_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	"""
	Scan a save file and extract campaign data

	:param game_id:
		Game ID
	:param request_data:
		Request data with save_dir key
	:param game_context:
		Game context
	:param save_file_service:
		Save file service
	:param game_service:
		Game service
	:return:
		Campaign data
	"""
	GAME_CONTEXT.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	save_dir = request_data.get("save_dir")
	if not save_dir:
		raise HTTPException(status_code=400, detail="save_dir is required")

	try:
		campaign_data = save_file_service.scan_hero_data(game, save_dir)
		return campaign_data
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/games/{game_id}/profiles/{profile_id}/scan")
@inject
async def scan_shops(
	game_id: int,
	profile_id: int,
	game_context: GameContext = Depends(get_game_context),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	"""
	Scan most recent save file for profile and sync shop inventories

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID
	:param game_context:
		Game context with schema information
	:param profile_service:
		Profile service
	:return:
		Counts dictionary
	"""
	import traceback

	GAME_CONTEXT.set(game_context)

	try:
		result = profile_service.scan_most_recent_save(profile_id)
		shops = result.shops
		return {
			"items": shops.items,
			"spells": shops.spells,
			"units": shops.units,
			"garrison": shops.garrison,
			"corrupted_data": shops.missed_data.model_dump() if shops.missed_data else None,
			"hero_inventory_items": result.hero_inventory.items
		}
	except FileNotFoundError as e:
		return JSONResponse(
			status_code=404,
			content={
				"detail": {
					"error": f"No matching save file: {str(e)}",
					"error_type": "FileNotFoundError",
					"error_traceback": traceback.format_exc()
				}
			}
		)
	except InvalidKbIdException as e:
		return JSONResponse(
			status_code=400,
			content={
				"detail": {
					"error": f"Invalid game data: {str(e)}",
					"error_type": "InvalidKbIdException",
					"error_traceback": traceback.format_exc()
				}
			}
		)
	except Exception as e:
		return JSONResponse(
			status_code=500,
			content={
				"detail": {
					"error": f"Scan failed: {str(e)}",
					"error_type": type(e).__name__,
					"error_traceback": traceback.format_exc()
				}
			}
		)


@router.patch("/games/{game_id}/profiles/{profile_id}/auto-scan")
@inject
async def update_profile_auto_scan(
	game_id: int,
	profile_id: int,
	is_enabled: bool,
	game_context: GameContext = Depends(get_game_context),
	profile_repository: IProfileRepository = Depends(Provide["profile_repository"])
) -> JSONResponse:
	"""
	Toggle auto-scan setting for a profile

	:param game_id:
		Game ID
	:param profile_id:
		Profile ID to update
	:param is_enabled:
		New auto-scan state
	:param game_context:
		Game context
	:param profile_repository:
		Profile repository
	:return:
		JSON response with updated state
	"""
	GAME_CONTEXT.set(game_context)

	try:
		profile = profile_repository.get_by_id(profile_id)
		if not profile:
			raise HTTPException(status_code=404, detail="Profile not found")

		profile.is_auto_scan_enabled = is_enabled
		profile_repository.update(profile)

		return JSONResponse(
			status_code=200,
			content={"id": profile_id, "is_auto_scan_enabled": is_enabled}
		)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
