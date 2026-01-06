from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

from src.domain.game.interfaces.IProfileService import IProfileService
from src.domain.game.interfaces.ISaveFileService import ISaveFileService
from src.domain.app.interfaces.IGameService import IGameService
from src.web.dependencies.game_context import get_game_context, GameContext
from src.domain.base.repositories.CrudRepository import _game_context
from src.domain.exceptions import InvalidKbIdException


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
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	try:
		save_dirs = save_file_service.list_save_directories(game.path, limit=100)
		return save_dirs
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to list saves: {str(e)}")


@router.post("/games/{game_id}/scan-save")
@inject
async def scan_save_file(
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
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	save_dir = request_data.get("save_dir")
	if not save_dir:
		raise HTTPException(status_code=400, detail="save_dir is required")

	try:
		campaign_data = save_file_service.scan_save_file(game.path, save_dir)
		return campaign_data
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/games/{game_id}/profiles/{profile_id}/scan")
@inject
async def scan_profile_save(
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

	_game_context.set(game_context)

	try:
		result = profile_service.scan_most_recent_save(profile_id)
		return {
			"items": result.items,
			"spells": result.spells,
			"units": result.units,
			"garrison": result.garrison,
			"corrupted_data": result.corrupted_data.model_dump() if result.corrupted_data else None
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
