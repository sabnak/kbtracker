from fastapi import APIRouter, Request, Form, Query, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.items.forms import ItemTrackForm
from src.domain.game.services import ItemTrackingService
from src.domain.profile.services.ProfileService import ProfileService


router = APIRouter(tags=["items"])
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/profiles/{profile_id}/items", response_class=HTMLResponse)
@inject
async def list_items(
	request: Request,
	profile_id: int,
	query: str = Query(default=""),
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	items = item_tracking_service.search_items(query)

	return templates.TemplateResponse(
		"pages/item_list.html",
		{
			"request": request,
			"profile": profile,
			"items": items,
			"query": query
		}
	)


@router.get("/profiles/{profile_id}/items/{item_id}/track", response_class=HTMLResponse)
@inject
async def track_item_form(
	request: Request,
	profile_id: int,
	item_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	items = item_tracking_service.search_items("")
	item = next((i for i in items if i.id == item_id), None)
	if not item:
		return RedirectResponse(url=f"/profiles/{profile_id}/items", status_code=303)

	locations = item_tracking_service.get_locations()

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


@router.get("/profiles/{profile_id}/tracked", response_class=HTMLResponse)
@inject
async def tracked_items(
	request: Request,
	profile_id: int,
	item_tracking_service: ItemTrackingService = Depends(Provide["item_tracking_service"]),
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	tracked = item_tracking_service.get_tracked_items(profile_id)

	return templates.TemplateResponse(
		"pages/tracked_items.html",
		{
			"request": request,
			"profile": profile,
			"tracked_items": tracked
		}
	)
