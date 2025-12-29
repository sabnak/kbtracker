from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.Container import Container
from src.core.DefaultInstaller import DefaultInstaller
from src.config import Settings


def create_app() -> FastAPI:
	settings = Settings()

	container = Container()
	container.config.from_dict(settings.model_dump())

	installer = DefaultInstaller(container)
	installer.install()

	app = FastAPI(title="King's Bounty Tracker", version="1.0.0")
	app.container = container

	app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

	from src.web.profiles.routes import router as profiles_router
	from src.web.scanner.routes import router as scanner_router
	from src.web.items.routes import router as items_router
	from src.web.games.routes import router as games_router

	app.include_router(profiles_router)
	app.include_router(scanner_router)
	app.include_router(items_router)
	app.include_router(games_router)

	return app


app = create_app()
