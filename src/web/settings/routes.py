from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from src.domain.app.entities.AppLanguage import AppLanguage
from src.domain.app.entities.Settings import Settings
from src.domain.app.interfaces.ISettingsService import ISettingsService
from src.web.settings.forms import SettingsForm
from src.web.template_filters import register_filters

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")
register_filters(templates)


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
			"errors": {},
			"AppLanguage": AppLanguage
		}
	)


@router.post("/settings")
@inject
async def save_settings(
	request: Request,
	scan_frequency: int = Form(...),
	saves_limit: int = Form(...),
	language: str = Form(...),
	settings_service: ISettingsService = Depends(Provide["settings_service"])
):
	try:
		form = SettingsForm(
			scan_frequency=scan_frequency,
			saves_limit=saves_limit,
			language=language
		)
		settings = Settings(
			scan_frequency=form.scan_frequency,
			saves_limit=form.saves_limit,
			language=AppLanguage[form.language]
		)
		settings_service.save_settings(settings)
		return RedirectResponse(url="/settings", status_code=303)
	except ValidationError as e:
		settings = settings_service.get_settings()
		errors = {err["loc"][0]: err["msg"] for err in e.errors()}
		return templates.TemplateResponse(
			"pages/settings.html",
			{
				"request": request,
				"settings": settings,
				"errors": errors,
				"AppLanguage": AppLanguage
			}
		)
