import os

from dotenv import load_dotenv

from .auth import SpotifyAuth
from .spotify import SpotifyAPI

load_dotenv(override=True)


spotify_auth = SpotifyAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
)


spotify = SpotifyAPI(auth=spotify_auth)
