from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from src.web.scanner.forms import ScanForm
from src.domain.game.services.ScannerService import ScannerService
from src.domain.profile.services.ProfileService import ProfileService
from src.config import Settings


router = APIRouter(tags=["scanner"])
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/profiles/{profile_id}/scan", response_class=HTMLResponse)
@inject
async def scan_form(
	request: Request,
	profile_id: int,
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	languages = [
		{"value": "ru", "label": "Russian"},
		{"value": "eng", "label": "English"},
		{"value": "ger", "label": "German"},
		{"value": "pol", "label": "Polish"}
	]

	return templates.TemplateResponse(
		"pages/scan.html",
		{"request": request, "profile": profile, "languages": languages}
	)


@router.post("/profiles/{profile_id}/scan")
@inject
async def scan_game_files(
	request: Request,
	profile_id: int,
	language: str = Form(...),
	scanner_service: ScannerService = Depends(Provide["scanner_service"]),
	profile_service: ProfileService = Depends(Provide["profile_service"])
):
	profile = profile_service.get_profile(profile_id)
	if not profile:
		return RedirectResponse(url="/", status_code=303)

	try:
		form_data = ScanForm(language=language)
		settings = Settings()

		result = scanner_service.scan_game_files(
			game_version=profile.game_version,
			language=form_data.language.value,
			game_data_path=settings.game_data_path
		)

		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"profile": profile,
				"success": True,
				"result": result
			}
		)
	except NotImplementedError as e:
		languages = [
			{"value": "ru", "label": "Russian"},
			{"value": "eng", "label": "English"},
			{"value": "ger", "label": "German"},
			{"value": "pol", "label": "Polish"}
		]
		return templates.TemplateResponse(
			"pages/scan.html",
			{
				"request": request,
				"profile": profile,
				"languages": languages,
				"error": str(e)
			}
		)
