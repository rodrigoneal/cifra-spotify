import httpx
from fastapi import status

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions.exceptions import AuthRetry
from src.cifra_spotify.app.schemas.me_schema import SpotifyUser
from src.cifra_spotify.app.schemas.search_schema import (
    PlaylistsResponse,
    SpotifySearchResponse,
)
from src.cifra_spotify.app.schemas.track_schema import SpotifyCurrentlyPlaying
from src.cifra_spotify.spotify.clients.spotify_api import SpotifyAPI
from src.cifra_spotify.spotify.clients.spotify_auth import SpotifyAuth
from src.cifra_spotify.spotify.retry_config import spotify_retry


class SpotifyClient:
    def __init__(self, auth: SpotifyAuth, client: httpx.AsyncClient):
        self.auth = auth
        self.client = client

    async def _request(self, url: str, params=None):
        token = await self.auth.ensure_token()

        try:
            resp = await self.client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10,
            )
        except httpx.RequestError as e:
            logger.error(f"[SpotifyClient] Erro de rede: {e}")
            raise AuthRetry("Erro de rede")

        if resp.status_code == status.HTTP_401_UNAUTHORIZED:
            logger.warning("[SpotifyClient] Token expirado. Atualizando…")
            await self.auth.refresh_access_token()
            raise AuthRetry()

        if resp.status_code not in (200, 204):
            msg = f"[SpotifyClient] Erro HTTP {resp.status_code} ao acessar {url}"
            logger.error(msg)
            raise AuthRetry(msg)

        if resp.status_code == 204:
            return None

        return resp.json()

    @spotify_retry()
    async def get_currently_playing(self) -> SpotifyCurrentlyPlaying:
        """
        Pega a musica tocando.
        """
        logger.debug("[SpotifyClient] Buscando musica tocando...")
        data = await self._request(SpotifyAPI.currently_playing())
        if data is None:
            return None
        return SpotifyCurrentlyPlaying.model_validate(data)

    @spotify_retry()
    async def get_me(self) -> SpotifyUser:
        """
        Pega o usuario logado.
        """
        logger.debug("[SpotifyClient] Buscando usuario logado...")
        data = await self._request(SpotifyAPI.me())
        return SpotifyUser.model_validate(data)

    @spotify_retry()
    async def search_track(self, name, limit=10, offset=0) -> SpotifyCurrentlyPlaying:
        """
        Pesquisa uma musica.
        """
        params = {"q": name, "type": "track", "limit": limit, "offset": offset}
        logger.debug(f"[SpotifyClient] Buscando musica {name} ")
        data = await self._request(SpotifyAPI.search(), params=params)
        return SpotifyCurrentlyPlaying.model_validate(data)

    @spotify_retry()
    async def get_my_playlists(self, limit=10, offset=0) -> PlaylistsResponse:
        """
        Pega as playlists do usuario logado.
        """
        logger.debug("[SpotifyClient] Buscando playlists...")
        params = {"limit": limit, "offset": offset}
        data = await self._request(SpotifyAPI.my_playlists(), params=params)
        return PlaylistsResponse.model_validate(data)

    @spotify_retry()
    async def search_playlist(self, name, limit=10, offset=0) -> SpotifySearchResponse:
        """
        Pesquisa uma playlist.
        """

        params = {"q": name, "type": "playlist", "limit": limit, "offset": offset}
        data = await self._request(SpotifyAPI.search(), params=params)

        logger.debug("[SpotifyClient] Playlist encontrada...")
        return SpotifySearchResponse.model_validate(data)
