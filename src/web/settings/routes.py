from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from src.domain.app.interfaces.ISettingsService import ISettingsService
from src.web.settings.forms import SettingsForm

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/settings", response_class=HTMLResponse)
@inject
async def get_settings(
	request: Request,
	settings_service: ISettingsService = Depends(Provide["settings_service"])
):
	settings = settings_service.get_settings()
	return templates.TemplateResponse(
		"pages/settings.html",
		{
			"request": request,
			"settings": settings,
			"errors": {}
		}
	)


@router.post("/settings")
@inject
async def save_settings(
	request: Request,
	sync_frequency: int = Form(...),
	saves_limit: int = Form(...),
	settings_service: ISettingsService = Depends(Provide["settings_service"])
):
	try:
		form = SettingsForm(
			sync_frequency=sync_frequency,
			saves_limit=saves_limit
		)
		settings_service.save_settings(form)
		return RedirectResponse(url="/settings", status_code=303)
	except ValidationError as e:
		settings = settings_service.get_settings()
		errors = {err["loc"][0]: err["msg"] for err in e.errors()}
		return templates.TemplateResponse(
			"pages/settings.html",
			{
				"request": request,
				"settings": settings,
				"errors": errors
			}
		)
