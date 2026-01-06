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


def create_app() -> FastAPI:
	container = Container()

	installer = DefaultInstaller(container)
	installer.install()

	app = FastAPI(title="King's Bounty Tracker", version="1.0.0")
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

	app.include_router(profiles_router)
	app.include_router(games_router)
	app.include_router(api_router)

	return app


app = create_app()
