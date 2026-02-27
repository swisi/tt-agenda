from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pathlib

from .config import Config
from . import database
from .interface.http.routes import router
from .models import seed_default_positions, seed_default_users


def create_app(config_class: type[Config] = Config) -> FastAPI:
    app = FastAPI(title="TT-Agenda v2", version="0.2.0")

    config = config_class
    app.state.config = config

    database.configure_database(config.DATABASE_URL)
    if config.AUTO_CREATE_DB:
        database.init_db()

    if database.SessionLocal is not None and (config.CREATE_DEFAULT_USERS or config.CREATE_DEFAULT_POSITIONS):
        db = database.SessionLocal()
        try:
            if config.CREATE_DEFAULT_USERS:
                seed_default_users(
                    db=db,
                    admin_username=config.DEFAULT_ADMIN_USERNAME,
                    admin_password=config.DEFAULT_ADMIN_PASSWORD,
                    coach_username=config.DEFAULT_COACH_USERNAME,
                    coach_password=config.DEFAULT_COACH_PASSWORD,
                )
            if config.CREATE_DEFAULT_POSITIONS:
                seed_default_positions(db)
        finally:
            db.close()

    app.include_router(router)
    # Mount package static/ directory at /static
    pkg_dir = pathlib.Path(__file__).resolve().parent
    static_dir = str(pkg_dir / "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    return app
