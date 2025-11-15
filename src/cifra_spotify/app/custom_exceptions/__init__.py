from fastapi import FastAPI

from . import exc_handler


def register_exception_handlers(app: FastAPI) -> FastAPI:
    app.add_exception_handler(
        exc_handler.CurrentTrackNotFoundException,
        exc_handler.current_track_not_found_exception_handler,
    )
    
    app.add_exception_handler(
        exc_handler.PlaylistSeachException,
        exc_handler.playlist_erro_handler
    )

    return app
