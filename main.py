from fastapi import FastAPI

from src.cifra_spotify.api import register_routers
from src.cifra_spotify.app.custom_exceptions import register_exception_handlers


def create_app():
    app = FastAPI()

    register_routers(app)
    register_exception_handlers(app)

    return app


app = create_app()
