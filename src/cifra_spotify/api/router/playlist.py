from typing import Annotated

from fastapi import APIRouter, Query, status

from src.cifra_spotify.api.deps import SPOTIFYDEPS
from src.cifra_spotify.app.custom_exceptions.exceptions import PlaylistSeachException
from src.cifra_spotify.app.schemas.search_schema import (
    PlaylistsResponse,
    SpotifySearchResponse,
)

router = APIRouter(prefix="/api/playlist", tags=["PLAYLIST"])


@router.get("/search_playlist", response_model=SpotifySearchResponse)
async def search_playlist(
    name: Annotated[str, Query(..., description="Nome da playlist")],
    limit: Annotated[int, Query(..., description="Limite de resultados")] = 10,
    offset: Annotated[int, Query(..., description="Offset de resultados")] = 0,
    spotify: SPOTIFYDEPS = None,
):
    response = await spotify.search_playlist(name=name, limit=limit, offset=offset)
    if response.status_code == status.HTTP_200_OK:
        return SpotifySearchResponse.model_validate(response.json())
    else:
        raise PlaylistSeachException(
            "Erro ao buscar playlist", status_code=response.status_code
        )


@router.get("/my_playlists", response_model=PlaylistsResponse)
async def my_playlists(
    spotify: SPOTIFYDEPS,
    limit: Annotated[int, Query(..., description="Limite de resultados")] = 10,
    offset: Annotated[int, Query(..., description="Offset de resultados")] = 0,
):
    response = await spotify.get_my_playlists(limit=limit, offset=offset)
    if response.status_code != status.HTTP_200_OK:
        raise PlaylistSeachException(
            "Erro ao buscar playlist", status_code=response.status_code
        )
    return PlaylistsResponse.model_validate(response.json())
