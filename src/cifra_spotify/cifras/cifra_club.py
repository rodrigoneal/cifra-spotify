from typing import TypedDict
from bs4 import BeautifulSoup
import httpx
from weasyprint import HTML
from src.cifra_spotify.cifras.cifra_base import Cifra, Instruments


class CifraType(TypedDict):
    cifra: str
    tom: str


class CifraClub(Cifra):
    url_base = "https://cifraclub.com.br/"

    async def _send_request(self, uri: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url = self.url_base + uri
            print(url)
            return await client.get(url, follow_redirects=True)

    def _mount_url(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
    ):
        singer = singer.replace(" ", "-").lower()
        music = music.replace(" ", "-").lower()
        instrument = instrument.value.lower()
        return f"{singer}/{music}/#instrument={instrument}"

    def extract_cifra(self, response: httpx.Response, tabs: bool = False) -> CifraType:
        soup = BeautifulSoup(response.text, "html.parser")
        tom_musica = soup.find("span", id="cifra_tom")
        tom_texto = tom_musica.get_text(strip=True) if tom_musica else ""
        pre = soup.find("pre")
        if not tabs:
            tablatures = pre.find_all("span", class_="tablatura")
            for t in tablatures:
                t.decompose()
        return {
            "tom": tom_texto,
            "cifra": str(pre),
        }

    async def get_cifra(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ):
        response = await self._send_request(self._mount_url(singer, music, instrument))
        return self.extract_cifra(response)

    def _format_html(self, cifra: str, tom: str) -> str:
        return f"""
        <html>
        <head>
        <meta charset="utf-8">
        <style>
        .cifra-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: flex-start;
        }}

        .tom {{
            font-weight: bold;
            min-width: max-content;
            font-size: 10px;
        }}

        pre {{
            display: inline-block;   /* AQUI É O SEGREDO */
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 9px;
            margin: 0;
            padding: 0;
        }}
        </style>
        </head>
        <body>

        <div class="cifra-container">
            <div class="tom">{tom}</div>
            {cifra}
        </div>

        </body>
        </html>
        """

    def _generate_pdf(self, html: str):
        return HTML(string=html).write_pdf()

    async def to_pdf(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
        tabs: bool = True,
    ) -> bytes:
        response = await self._send_request(self._mount_url(singer, music, instrument))
        cifra = self.extract_cifra(response, tabs)
        html_cifra = self._format_html(**cifra)
        return self._generate_pdf(html_cifra)
