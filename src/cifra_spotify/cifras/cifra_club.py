import asyncio

import httpx
from weasyprint import HTML

from src.cifra_spotify.cifras.cifra_base import Cifra, Instruments
from src.cifra_spotify.types import cifra as cifra_type

from .parsers.cifraclub import parse_cifra_page
from .render.cifraclub import render_html_document
from .util import slugify_cifraclub


def divisor_medley_default(music_name: str, divisor: str = "/") -> list[str]:
    return music_name.split(divisor)


class CifraClub(Cifra):
    url_base = "https://cifraclub.com.br/"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True)

    async def _fetch_page(self, uri: str) -> httpx.Response:
        url = self.url_base + uri
        print(url)
        return await self.client.get(url, follow_redirects=True)

    def _build_url(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
    ):
        singer = slugify_cifraclub(singer)
        music = slugify_cifraclub(music)
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
        cifras = await asyncio.gather(
            *[
                self._fetch_cifra(
                    singer=singer, music=music, tabs=tabs, instrument=instrument
                )
                for music in musics
            ]
        )
        return render_html_document(cifras)

    async def generate_pdf(
        self,
        html: str,
    ) -> bytes:
        return await asyncio.to_thread(self._generate_pdf, html)
