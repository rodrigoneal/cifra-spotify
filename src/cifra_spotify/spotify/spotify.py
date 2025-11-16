from typing import Any

import httpx

from src.cifra_spotify.app.core.logger import logger

from .auth import SpotifyAuth


class SpotifyAPI:
    """
    Wrapper para chamadas à API Web do Spotify.

    Esta classe fornece métodos convenientes para acessar
    o usuário logado, faixa atual, playlists e buscas.
    """

    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, auth: SpotifyAuth, request_timeout: int = 10):
        """
        Inicializa o cliente da API do Spotify.

        Args:
            auth (SpotifyAuth): Instância responsável por obter e renovar tokens OAuth.
            request_timeout (int): Timeout padrão para requisições HTTP, em segundos.
        """
        self.auth = auth
        self.request_timeout = request_timeout
        self.client = httpx.AsyncClient(timeout=request_timeout)

    async def _send_request(
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        """
        Envia uma requisição GET autenticada à API do Spotify.

        Args:
            path (str): Caminho relativo dentro da API (ex: "me", "search").
            params (dict, optional): Parâmetros de querystring.

        Returns:
            httpx.Response: Resposta completa da requisição HTTP.
        """

        token = await self.auth.ensure_token()
        logger.debug("Sending request to Spotify API...")

        return await self.client.get(
            f"{self.BASE_URL}/{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def me(self) -> httpx.Response:
        """
        Obtém informações do usuário autenticado.

        Returns:
            httpx.Response: Dados do usuário logado ("current user profile").
        """
        logger.info("Requesting current user profile...")
        return await self._send_request("me")

    async def get_current_track(self) -> httpx.Response:
        """
        Obtém a faixa que está tocando no momento.

        Returns:
            httpx.Response: Informações sobre a música atual,
                incluindo posição, dispositivo e status do player.
        """
        logger.debug("Requesting current track...")
        return await self._send_request("me/player/currently-playing")

    async def search_track(
        self, name: str, limit: int = 10, offset: int = 0
    ) -> httpx.Response:
        """
        Busca faixas por nome.

        Args:
            name (str): Nome da música ou trecho da busca.
            limit (int): Número máximo de resultados.
            offset (int): Número de itens para ignorar (paginação).

        Returns:
            httpx.Response: Resultado da busca contendo tracks.
        """
        logger.info(f"Searching for track: {name}, limit: {limit}, offset: {offset}")
        params = {"q": name, "type": "track", "limit": limit, "offset": offset}
        return await self._send_request("search", params=params)

    async def get_my_playlists(
        self, limit: int = 10, offset: int = 0
    ) -> httpx.Response:
        """
        Obtém as playlists do usuário autenticado.

        Args:
            limit (int): Número máximo de playlists retornadas.
            offset (int): Offset para paginação.

        Returns:
            httpx.Response: Lista de playlists do usuário.
        """
        logger.info(f"Requesting playlists, limit: {limit}, offset: {offset}")
        params = {"limit": limit, "offset": offset}
        return await self._send_request("me/playlists", params=params)

    async def search_playlist(
        self, name: str, limit: int = 10, offset: int = 0
    ) -> httpx.Response:
        """
        Busca playlists na API do Spotify.

        Args:
            name (str): Nome ou palavra-chave da playlist.
            limit (int): Número máximo de resultados.
            offset (int): Offset para paginação.

        Returns:
            httpx.Response: Resultado da busca contendo playlists.
        """
        params = {
            "q": name,
            "type": "playlist",
            "limit": limit,
            "offset": offset,
        }
        logger.info(f"Searching for playlist: {name}, limit: {limit}, offset: {offset}")
        return await self._send_request("search", params=params)

    async def aclose(self):
        """
        Fecha o cliente HTTP persistente.

        Deve ser chamado no shutdown da aplicação para liberar recursos.
        """
        logger.info("Closing HTTP client...")
        await self.client.aclose()
