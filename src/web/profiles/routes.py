from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.profiles.forms import ProfileCreateForm
from src.domain.game.IGameService import IGameService
from src.domain.profile.IProfileService import IProfileService
from src.web.dependencies.game_context import get_game_context, GameContext
from src.domain.CrudRepository import _game_context


router = APIRouter(tags=["profiles"])
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@inject
async def index(
	request: Request,
	profile_service: IProfileService = Depends(Provide["profile_service"]),
	game_service: IGameService = Depends(Provide["game_service"])
):
	profiles = profile_service.list_profiles()

	profiles_data = []
	for profile in profiles:
		game = game_service.get_game(profile.game_id)
		profiles_data.append({
			"profile": profile,
			"game": game
		})

	return templates.TemplateResponse(
		"pages/index.html",
		{"request": request, "profiles_data": profiles_data}
	)


@router.get("/games/{game_id}/profiles/create", response_class=HTMLResponse)
@inject
async def create_profile_form(
	request: Request,
	game_id: int,
	game_context: GameContext = Depends(get_game_context),
	game_service: IGameService = Depends(Provide["game_service"])
):
	_game_context.set(game_context)

	game = game_service.get_game(game_id)
	if not game:
		return RedirectResponse(url="/games", status_code=303)

	return templates.TemplateResponse(
		"pages/profile_create.html",
		{
			"request": request,
			"game": game
		}
	)


@router.post("/games/{game_id}/profiles")
@inject
async def create_profile(
	game_id: int,
	name: str = Form(...),
	game_context: GameContext = Depends(get_game_context),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	_game_context.set(game_context)

	form_data = ProfileCreateForm(name=name, game_id=game_id)
	profile_service.create_profile(form_data.name)
	return RedirectResponse(url=f"/games/{game_id}/items", status_code=303)


@router.post("/games/{game_id}/profiles/{profile_id}/delete")
@inject
async def delete_profile(
	game_id: int,
	profile_id: int,
	game_context: GameContext = Depends(get_game_context),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	_game_context.set(game_context)

	profile_service.delete_profile(profile_id)
	return RedirectResponse(url=f"/games/{game_id}/items", status_code=303)
