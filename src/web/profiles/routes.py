from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.profiles.forms import ProfileCreateForm
from src.domain.game.IGameService import IGameService
from src.domain.profile.IProfileService import IProfileService


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


@router.get("/profiles/create", response_class=HTMLResponse)
@inject
async def create_profile_form(
	request: Request,
	game_service: IGameService = Depends(Provide["game_service"])
):
	games = game_service.list_games()
	return templates.TemplateResponse(
		"pages/profile_create.html",
		{
			"request": request,
			"games": games
		}
	)


@router.post("/profiles/create")
@inject
async def create_profile(
	name: str = Form(...),
	game_id: int = Form(...),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	form_data = ProfileCreateForm(name=name, game_id=game_id)
	profile_service.create_profile(form_data.name, form_data.game_id)
	return RedirectResponse(url="/", status_code=303)


@router.post("/profiles/{profile_id}/delete")
@inject
async def delete_profile(
	profile_id: int,
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	profile_service.delete_profile(profile_id)
	return RedirectResponse(url="/", status_code=303)
