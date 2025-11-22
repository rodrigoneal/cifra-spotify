import httpx

from src.cifra_spotify.app.core.logger import logger


class CifraClubHttpClient:
    """Cliente HTTP para o Cifra Club"""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def fetch_page(self, url: str) -> httpx.Response:
        """Realiza a requisição no site

        Arguments:
            url -- url da pagina

        Returns:
            Response -- Resposta da requisição
        """
        logger.info(f"Fetching page: {url}")
        return await self.client.get(url, follow_redirects=True)
