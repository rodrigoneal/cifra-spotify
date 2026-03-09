from typing import Annotated

from fastapi import APIRouter, Query

from cifra_spotify.api.deps import SPOTIFYDEPS
from cifra_spotify.cifras.cifra_base import Instruments
from cifra_spotify.cifras.cifra_club import CifraClub
from cifra_spotify.cifras.enum import SitesCifra
from cifra_spotify.cifras.parsers.spotify import get_current_track_with_genres
from cifra_spotify.cifras.schemas.response import ChordSearchResponse
from cifra_spotify.cifras.util import improve_response

router = APIRouter(prefix="/api/cifra", tags=["CIFRA"])


@router.get("/", response_model=ChordSearchResponse)
async def cifra_by_current_track(
    spotify: SPOTIFYDEPS,
    site: Annotated[
        SitesCifra,
        Query(description="Website where the musical score will be searched."),
    ] = SitesCifra.CIFRAS_CLUB,
    instrument: Annotated[
        Instruments,
        Query(
            description="Instrument used to search the musical score.",
        ),
    ] = Instruments.GUITAR,
):
    """Get the cifra of the current track playing on the authenticated user's Spotify account."""

    song_data = await get_current_track_with_genres(spotify)

    cifra_club = CifraClub()

    items = await cifra_club.search_musics(
        singer=song_data.artist_name,
        music=song_data.track_name,
        instrument=instrument,
    )

    return improve_response(items, song_data)
