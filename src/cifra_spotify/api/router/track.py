from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.cifra_spotify.api.deps import SPOTIFYDEPS
from src.cifra_spotify.app.custom_exceptions.exceptions import \
    CurrentTrackNotFoundException
from src.cifra_spotify.app.schemas.track_schema import SpotifyCurrentlyPlaying
from src.cifra_spotify.app.schemas.track_search_schema import \
    SpotifyTrackSearchResponse

router = APIRouter(prefix="/api/track", tags=["TRACK"])


@router.get(
    "/current_track",
    response_model=SpotifyCurrentlyPlaying,
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.NOT_FOUND: {
            "response": {"message": "Track not found or not playing"},
            "description": "Track not found or not playing",
        }
    },
)
async def current_track(spotify: SPOTIFYDEPS):
    """
    Get the track currently playing on the authenticated user's Spotify account.

    This endpoint calls Spotify's playback API and returns detailed information
    about the current track, including title, artists, album, and playback status.

    If no track is playing, a 404 response is returned.
    """
    response = await spotify.get_current_track()
    if response.status_code == HTTPStatus.OK:
        return response.json()
    elif response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.NO_CONTENT):
        raise CurrentTrackNotFoundException(
            message="No track is currently playing", status_code=HTTPStatus.NOT_FOUND
        )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )


@router.get("/search_track", response_model=SpotifyTrackSearchResponse)
async def search_track(
    spotify: SPOTIFYDEPS,
    name: Annotated[str, Query(..., description="Nome da musica")],
    limit: Annotated[int, Query(..., description="Limite de resultados")] = 10,
    offset: Annotated[int, Query(..., description="Offset de resultados")] = 0,
):
    """
    Search for tracks on Spotify by name.

    This endpoint queries Spotify's search API and returns a list of tracks
    matching the given name. The results include track metadata such as title,
    artists, album, and Spotify IDs, which can later be used to fetch lyrics,
    chords, or playback details.

    Pagination is supported through the `limit` and `offset` parameters.
    """
    response = await spotify.search_track(name=name, limit=limit, offset=offset)
    return SpotifyTrackSearchResponse.model_validate(response.json())
