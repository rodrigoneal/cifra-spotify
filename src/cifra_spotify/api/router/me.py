from fastapi import APIRouter

from src.cifra_spotify.app.schemas.me_schema import SpotifyUser
from src.cifra_spotify.api.deps import SPOTIFYDEPS

router = APIRouter(prefix="/api", tags=["ME"])


@router.get("/", response_model=SpotifyUser)
async def me(spotify: SPOTIFYDEPS = None):
    """
    Return information about the authenticated Spotify user.

    This endpoint calls Spotify's `/me` API using the user's OAuth access token
    and returns basic profile information such as display name, ID, profile image,
    and follower data.
    """
    response = await spotify.me()
    return SpotifyUser.model_validate(response.json())
