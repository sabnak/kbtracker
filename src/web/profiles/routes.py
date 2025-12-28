from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.profiles.forms import ProfileCreateForm
from src.domain.filesystem.services.GamePathService import GamePathService
from src.domain.profile.services.ProfileService import ProfileService


router = APIRouter(tags=["profiles"])
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@inject
async def index(
	request: Request,
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profiles = profile_service.list_profiles()
	return templates.TemplateResponse(
		"pages/index.html",
		{"request": request, "profiles": profiles}
	)


@router.get("/profiles/create", response_class=HTMLResponse)
@inject
async def create_profile_form(
	request: Request,
	game_path_service: GamePathService = Depends(Provide["game_path_service"])
):
	available_paths = game_path_service.get_available_game_paths()
	return templates.TemplateResponse(
		"pages/profile_create.html",
		{
			"request": request,
			"available_game_paths": available_paths
		}
	)


@router.post("/profiles/create")
@inject
async def create_profile(
	name: str = Form(...),
	game_path: str = Form(...),
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	form_data = ProfileCreateForm(name=name, game_path=game_path)
	profile_service.create_profile(form_data.name, form_data.game_path)
	return RedirectResponse(url="/", status_code=303)


@router.post("/profiles/{profile_id}/delete")
@inject
async def delete_profile(
	profile_id: int,
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile_service.delete_profile(profile_id)
	return RedirectResponse(url="/", status_code=303)
