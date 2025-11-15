from fastapi import FastAPI

from .router import auth, me, playlist, track, webhooks


def register_routers(app: FastAPI) -> FastAPI:
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(playlist.router)
    app.include_router(track.router)
    app.include_router(webhooks.router)

    return app
