from typing import Annotated

from fastapi import APIRouter, Query, status

from src.cifra_spotify.api.deps import SPOTIFYDEPS
from src.cifra_spotify.app.custom_exceptions.exceptions import \
    PlaylistSeachException
from src.cifra_spotify.app.schemas.search_schema import (PlaylistsResponse,
                                                         SpotifySearchResponse)

router = APIRouter(prefix="/api/playlist", tags=["PLAYLIST"])


@router.get("/search_playlist", response_model=SpotifySearchResponse)
async def search_playlist(
    spotify: SPOTIFYDEPS,
    name: Annotated[str, Query(..., description="Nome da playlist")],
    limit: Annotated[int, Query(..., description="Limite de resultados")] = 10,
    offset: Annotated[int, Query(..., description="Offset de resultados")] = 0,
):
    """
    Search playlists on Spotify.

    This endpoint searches for playlists using the Spotify Web API based on the provided
    name. Results can be paginated using the `limit` and `offset` parameters.
    """
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
    """
    Get the authenticated user's playlists.

    This endpoint returns the playlists owned or followed by the logged-in user.
    Pagination is supported through the `limit` and `offset` parameters.
    """
    response = await spotify.get_my_playlists(limit=limit, offset=offset)
    if response.status_code != status.HTTP_200_OK:
        raise PlaylistSeachException(
            "Erro ao buscar playlist", status_code=response.status_code
        )
    return PlaylistsResponse.model_validate(response.json())
