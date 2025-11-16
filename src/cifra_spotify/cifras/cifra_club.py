from .render.cifraclub import render_html_document
from .parsers.cifraclub import parse_cifra_page
from src.cifra_spotify.types import cifra as cifra_type
import httpx
from weasyprint import HTML
from src.cifra_spotify.cifras.cifra_base import Cifra, Instruments


def divisor_medley_default(music_name: str, divisor: str = "/") -> list[str]:
    return music_name.split(divisor)


class CifraClub(Cifra):
    url_base = "https://cifraclub.com.br/"

    async def _fetch_page(self, uri: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self.url_base + uri
            return await client.get(url, follow_redirects=True)

    def _build_url(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
    ):
        singer = singer.replace(" ", "-").lower()
        music = music.replace(" ", "-").lower()
        instrument = instrument.value.lower()
        return f"{singer}/{music}/#instrument={instrument}"

    async def _fetch_cifra(
        self,
        singer: str,
        music: str,
        tabs: bool,
        instrument: Instruments = Instruments.GUITAR,
    ):
        response = await self._fetch_page(self._build_url(singer, music, instrument))
        return parse_cifra_page(response, tabs)

    def _generate_pdf(self, html: str):
        return HTML(string=html).write_pdf()

    async def generate_html(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
        tabs: bool = True,
        medley_splitter: cifra_type.MedleySplitter | None = divisor_medley_default,
    ) -> str:
        cifras = []
        if medley_splitter:
            musics = medley_splitter(music)
        else:
            musics = [music]
        for music in musics:
            cifra = await self._fetch_cifra(
                singer=singer, music=music, tabs=tabs, instrument=instrument
            )
            cifras.append(cifra)
        return render_html_document(cifras)

    async def generate_pdf(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
        tabs: bool = True,
        medley_splitter: cifra_type.MedleySplitter | None = divisor_medley_default,
    ) -> bytes:
        html = await self.generate_html(
            singer, music, instrument, tabs, medley_splitter
        )
        return self._generate_pdf(html)
