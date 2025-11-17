from fastapi import FastAPI

from .router import auth, track, webhooks


def register_routers(app: FastAPI) -> FastAPI:
    app.include_router(auth.router)
    app.include_router(track.router)
    app.include_router(webhooks.router)

    return app
