from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException, RequestValidationError

from src.core.Config import Config
from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller
from src.core.logging_config import setup_logging

from src.web.middleware.request_context import RequestContextMiddleware
from src.web.exception_handlers import (
	kbtracker_exception_handler,
	http_exception_handler,
	validation_error_handler,
	generic_exception_handler
)
from src.domain.exceptions import KBTrackerException


load_dotenv()


def create_app() -> FastAPI:
	container = Container()

	installer = DefaultInstaller(container)
	installer.install()

	@asynccontextmanager
	async def lifespan(app: FastAPI):
		from src.web.profiles.routes import templates as profiles_templates
		from src.web.games.routes import templates as games_templates
		from src.web.settings.routes import templates as settings_templates
		from src.web.exception_handlers import templates as error_templates
		from src.web.template_filters import install_translations

		translation_service = container.translation_service()

		for templates in [games_templates, settings_templates, profiles_templates, error_templates]:
			install_translations(templates, translation_service)

		yield

	app = FastAPI(
		title="King's Bounty Tracker",
		version="1.0.0",
		lifespan=lifespan
	)
	app.container = container

	# Add request context middleware
	app.add_middleware(RequestContextMiddleware)

	# Register exception handlers
	app.add_exception_handler(KBTrackerException, kbtracker_exception_handler)
	app.add_exception_handler(HTTPException, http_exception_handler)
	app.add_exception_handler(RequestValidationError, validation_error_handler)
	app.add_exception_handler(Exception, generic_exception_handler)

	app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

	from src.web.profiles.routes import router as profiles_router
	from src.web.games.routes import router as games_router
	from src.web.api.routes import router as api_router
	from src.web.settings.routes import router as settings_router

	app.include_router(profiles_router)
	app.include_router(games_router)
	app.include_router(api_router)
	app.include_router(settings_router)

	return app


app = create_app()
