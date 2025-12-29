from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide

from src.web.games.forms import GameCreateForm
from src.domain.filesystem.IGamePathService import IGamePathService
from src.domain.game.IGameService import IGameService


router = APIRouter(tags=["games"])
templates = Jinja2Templates(directory="src/web/templates")


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
