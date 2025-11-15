from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.cifra_spotify.api.deps import SPOTIFYDEPS
from src.cifra_spotify.app.custom_exceptions.exceptions import (
    CurrentTrackNotFoundException,
)
from src.cifra_spotify.app.schemas.track_schema import (
    CurrentTrackNotFound,
    SpotifyCurrentlyPlaying,
)

router = APIRouter(prefix="/api/track", tags=["TRACK"])


@router.get(
    "/current_track",
    response_model=SpotifyCurrentlyPlaying,
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.NOT_FOUND: {
            "model": CurrentTrackNotFound,
            "description": "Track not found or not playing",
        }
    },
)
async def current_track(spotify: SPOTIFYDEPS):
    """
    Retrieve the track currently being played on the user's Spotify account.

    This endpoint communicates with Spotify's Web API to fetch playback
    information for the authenticated user. If a track is currently playing,
    detailed information such as the track name, artists, album, playback
    status, and media metadata is returned.

    If no track is playing or Spotify returns an empty response, a
    `CurrentTrackNotFoundException` is raised, resulting in a 404 response
    containing a structured error (`CurrentTrackNotFound`).

    ### Returns
    - **200 OK**: A `SpotifyCurrentlyPlaying` model containing detailed
      information about the currently playing track.
    - **404 Not Found**: A `CurrentTrackNotFound` model indicating that no
      track is currently playing.

    ### Errors
    - `CurrentTrackNotFoundException`: Raised when Spotify returns
      204 (No Content) or 404 (Not Found).
    """
    response = await spotify.get_current_track()
    if response.status_code == HTTPStatus.OK:
        return response.json()
    elif response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.NO_CONTENT):
        raise CurrentTrackNotFoundException(
            is_playing=False,
            currently_playing_type="track",
        )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )


@router.get("/search_track")
async def search_track(name: str, limit: int = 10, spotify: SPOTIFYDEPS = None):
    return await spotify.search_track(name, limit)
