import asyncio

from src.cifra_spotify.app.schemas.cifraclub.cifraclub_schema import (
    CifraTransportSchema,
)
from src.cifra_spotify.cifras.cifra_club.render.render import (
    CifraClubHtmlRenderer,
    CifraClubPdfRenderer,
)


class Cifra:
    def __init__(self, cifra: list[CifraTransportSchema]) -> None:
        self.cifra = cifra
        self.render_pdf = CifraClubPdfRenderer()
        self.render_html = CifraClubHtmlRenderer()

    async def to_pdf(self) -> str:
        return await asyncio.to_thread(self.render_pdf.render, self.cifra)

    async def to_html(self) -> str:
        return asyncio.to_thread(self.render_html.render, self.cifra)
