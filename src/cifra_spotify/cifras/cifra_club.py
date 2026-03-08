import asyncio

import httpx
from weasyprint import HTML

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.cifras.cifra_base import Cifra, Instruments
from src.cifra_spotify.types import cifra as cifra_type

from .parsers.cifraclub import parse_cifra_page
from .render.cifraclub import render_html_document
from .util import (
    compare_artist_name,
    compare_track,
    normalize_track_title,
)


def divisor_medley_default(music_name: str, divisor: str = "/") -> list[str]:
    return [music.strip() for music in music_name.split(divisor)]


class CifraClub(Cifra):
    url_base = "https://cifraclub.com.br/"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True)

    async def _fetch_page(self, uri: str) -> httpx.Response:
        url = self.url_base + uri
        logger.info(f"Fetching page: {url}")
        return await self.client.get(url, follow_redirects=True)

    def _build_url(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
    ):
        instrument_str = instrument.value.lower()
        logger.debug(f"Building URL: {singer}/{music}/#instrument={instrument_str}")
        return f"{singer}/{music}/#instrument={instrument_str}"

    async def _fetch_cifra(
        self,
        singer: str,
        music: str,
        tabs: bool,
        instrument: Instruments = Instruments.GUITAR,
    ):
        logger.info(f"Fetching cifra: {singer} - {music}")
        url = self._build_url(singer, music, instrument)
        response = await self._fetch_page(url)
        response.raise_for_status()
        cifra_page = parse_cifra_page(response, tabs)
        cifra_page["url"] = self.url_base + url
        return cifra_page

    def _generate_pdf(self, html: str):
        logger.debug("Generating PDF...")
        return HTML(string=html).write_pdf()

    def get_music_tone(self, music: str) -> str:
        return music

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
        logger.info("Rendering HTML...")
        return render_html_document(cifras)

    async def generate_pdf(
        self,
        html: str,
    ) -> bytes:
        logger.info("Generating PDF...")
        return await asyncio.to_thread(self._generate_pdf, html)

    async def search_api_cifra(
        self,
        music: str,
    ):
        music_slug = normalize_track_title(music)
        logger.info(f"Searching cifra: {music_slug}")
        url = "https://solr.sscdn.co/cc/c7/"
        response = await self.client.get(url, params={"q": music_slug})
        response.raise_for_status()
        return response

    async def search_musics(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
        tabs: bool = True,
        medley_splitter: cifra_type.MedleySplitter | None = divisor_medley_default,
    ):
        musics = medley_splitter(music)
        all_music = []
        for music in musics:
            cifra_result = await self.search_api_cifra(music)
            urls_cifras = []
            if cifra_result:
                for cifra in cifra_result.json()["response"]["docs"]:
                    try:
                        music_api_name = cifra["txt"]
                        singer_api_name = cifra["art"]
                        singer_dns = cifra["dns"]
                        music_url_api = cifra["url"]
                    except KeyError:
                        continue
                    music_match_result = compare_track(
                        music_api_name, music, threshold=80
                    )
                    singer_match_result = compare_artist_name(
                        singer_api_name, singer, threshold=80
                    )
                    if (
                        not music_match_result["match"]
                        or not singer_match_result["match"]
                    ):
                        logger.info(
                            f"Music not found: {music_api_name} - {singer_api_name}"
                        )
                        continue
                    else:
                        urls_cifras.append(
                            {
                                "url": music_url_api,
                                "singer": singer_dns,
                                "music": music_api_name,
                            }
                        )
                        break
            all_music.extend(urls_cifras)

        return await asyncio.gather(
            *[
                self._fetch_cifra(
                    singer=music["singer"],
                    music=music["url"],
                    tabs=tabs,
                    instrument=instrument,
                )
                for music in all_music
            ]
        )
