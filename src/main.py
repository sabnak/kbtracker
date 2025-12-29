from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller
from src.config import Settings
from src.web.exception_handlers import (
	duplicate_entity_exception_handler,
	entity_not_found_exception_handler,
	database_operation_exception_handler
)
from src.domain.exceptions import (
	DuplicateEntityException,
	EntityNotFoundException,
	DatabaseOperationException
)


def create_app() -> FastAPI:
	settings = Settings()

	container = Container()
	container.config.from_dict(settings.model_dump())

	installer = DefaultInstaller(container)
	installer.install()

	app = FastAPI(title="King's Bounty Tracker", version="1.0.0")
	app.container = container

	app.add_exception_handler(
		DuplicateEntityException,
		duplicate_entity_exception_handler
	)
	app.add_exception_handler(
		EntityNotFoundException,
		entity_not_found_exception_handler
	)
	app.add_exception_handler(
		DatabaseOperationException,
		database_operation_exception_handler
	)

	app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

	from src.web.profiles.routes import router as profiles_router
	from src.web.games.routes import router as games_router

	app.include_router(profiles_router)
	app.include_router(games_router)

	return app


app = create_app()
