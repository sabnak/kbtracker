from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.profiles.forms import ProfileCreateForm, ItemTrackForm
from src.domain.game.IGameService import IGameService
from src.domain.profile.IProfileService import IProfileService
from src.domain.game.services import ItemTrackingService


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


@router.get("/profiles/{profile_id}/items/{item_id}/track", response_class=HTMLResponse)
@inject
async def track_item_form(
	request: Request,
	profile_id: int,
	item_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: IProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	items = item_tracking_service.search_items(profile.game_id, "")
	item = next((i for i in items if i.id == item_id), None)
	if not item:
		return RedirectResponse(url=f"/profiles/{profile_id}/tracked", status_code=303)

	locations = item_tracking_service.get_locations(profile.game_id)

	return templates.TemplateResponse(
		"pages/item_track.html",
		{
			"request": request,
			"profile": profile,
			"item": item,
			"locations": locations
		}
	)


@router.post("/profiles/{profile_id}/items/{item_id}/track")
@inject
async def track_item(
	profile_id: int,
	item_id: int,
	shop_id: int = Form(...),
	count: int = Form(default=1),
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"])
):
	form_data = ItemTrackForm(item_id=item_id, shop_id=shop_id, count=count)

	item_tracking_service.link_item_to_shop(
		profile_id=profile_id,
		item_id=form_data.item_id,
		shop_id=form_data.shop_id,
		count=form_data.count
	)

	return RedirectResponse(url=f"/profiles/{profile_id}/tracked", status_code=303)
