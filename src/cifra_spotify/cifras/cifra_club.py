from bs4 import BeautifulSoup
import httpx
from src.cifra_spotify.cifras.cifra_base import Cifra, Instruments


class CifraClub(Cifra):
    url_base = "https://cifraclub.com.br/"

    async def _send_request(self, uri: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self.url_base + uri
            return await client.get(url, follow_redirects=True)

    def _mount_url(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ):
        singer = singer.replace(" ", "-").lower()
        music = music.replace(" ", "-").lower()
        instrument = instrument.value.lower()
        return f"{singer}/{music}/#instrument={instrument}"
    
    def extract_cifra(self, response: httpx.Response) -> str:
        soup = BeautifulSoup(response.text, "html.parser")
        soup.find("pre")
        breakpoint()

    async def get_cifra(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ):
        response =  await self._send_request(self._mount_url(singer, music, instrument))
        return self.extract_cifra(response)
