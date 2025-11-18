from pydantic import BaseModel
from typing_extensions import Literal


class LoginUrl(BaseModel):
    login_url: str
    app: Literal["spotify"] = "spotify"


class SpotifyToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: float  # timestamp unix
    token_type: str = "Bearer"
