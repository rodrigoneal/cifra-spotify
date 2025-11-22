from fastapi import FastAPI


def register_routers(app: FastAPI) -> FastAPI:
    from .auth import router as auth_router
    from .cifra import router as cifra_router
    from .track import router as track_router
    from .webhook import router as webhook_router

    app.include_router(auth_router)
    app.include_router(webhook_router)
    app.include_router(track_router)
    app.include_router(cifra_router)
    return app
