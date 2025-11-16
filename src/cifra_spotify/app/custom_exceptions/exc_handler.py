from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import (
    CurrentTrackNotFoundException,
    PlaylistSeachException,
    UserNotAuthenticatedException,
)


def current_track_not_found_exception_handler(
    request: Request, exc: CurrentTrackNotFoundException
):
    return JSONResponse(content=exc.message, status_code=exc.status_code)


def playlist_erro_handler(request: Request, exc: PlaylistSeachException):
    return JSONResponse(content=exc.message, status_code=exc.status_code)


def user_not_authenticated_exception_handler(
    request: Request, exc: UserNotAuthenticatedException
):
    return JSONResponse(content=exc.message, status_code=exc.status_code)
