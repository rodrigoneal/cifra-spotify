from weasyprint import HTML

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.schemas.cifraclub.cifraclub_schema import (
    CifraTransportSchema,
)


class CifraClubHtmlRenderer:
    def _render_header(self) -> str:
        logger.debug("Rendering header...")
        return """
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {
                margin: 15px;
                font-family: Arial, sans-serif;
            }

            /* Container de colunas com linha separadora */
            .songbook {
                column-count: 2;
                column-gap: 20px;
                column-rule: 1px solid #ccc; /* linha entre as colunas */
            }

            /* Cada música */
            .musica {
                break-inside: avoid;
                page-break-inside: avoid;
                margin-bottom: 18px;
            }

            .titulo {
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid #999;
                padding-bottom: 2px;
                margin-bottom: 4px;
            }

            .tom {
                font-size: 9px;
                font-weight: bold;
                color: #444;
                margin-bottom: 3px;
            }

            /* Evitar quebra de linha dentro do acorde */
            b {
                white-space: nowrap;
            }

            pre {
                font-family: "Courier New", monospace;
                font-size: 8.8px;
                line-height: 1.16;
                white-space: pre-wrap;
                margin: 0;
                padding: 0;
            }

            hr {
                border: none;
                border-top: 1px solid #ccc;
                margin: 12px 0;
                break-inside: avoid;
            }
        </style>
        </head>
        <body>
        <div class="songbook">
        """

    def _render_song_section(self, song: CifraTransportSchema) -> str:
        logger.debug("Rendering song section...")
        return f"""
        <div class="musica">
            <div class="titulo">{song.music_name}</div>
            <div class="tom">Tom: {song.tom.replace("tom:", "")}</div>
            {song.cifra}
            <hr>
        </div>
        """

    def _render_footer(self) -> str:
        logger.debug("Rendering footer...")
        return """
        </div>
        </body>
        </html>
        """

    def render(self, songs: list[CifraTransportSchema]) -> str:
        html = self._render_header()

        for song in songs:
            logger.debug(f"Rendering song: {song.music_name}")
            html += self._render_song_section(song)

        html += self._render_footer()
        return html


class CifraClubPdfRenderer:
    def render(self, songs: list[CifraTransportSchema]) -> bytes:
        html = CifraClubHtmlRenderer().render(songs)
        logger.debug("Generating PDF from HTML...")
        return HTML(string=html).write_pdf()
