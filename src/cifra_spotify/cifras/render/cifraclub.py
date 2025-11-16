from src.cifra_spotify.types import cifra as cifra_type


def _render_header() -> str:
    return """
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        .bloco-musica {
            page-break-inside: avoid;
        }
        .musica {
            margin-bottom: 20px;
            page-break-inside: avoid;
        }

        .titulo {
            font-size: 14px;
            font-weight: bold;
        }

        .tom {
            font-weight: bold;
            font-size: 10px;
            margin-bottom: 4px;
        }

        .cifra-container {
            page-break-inside: avoid;
        }

        pre {
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 9px;
            margin: 0;
            padding: 0;
        }
        body {
            margin: 10px;
        }
    </style>
    </head>
    <body>
    """


def _render_song_section(music_name: str, tom: str, cifra: str) -> str:
    return f"""
    <div class="musica">
        <div class="bloco-musica">
            <div class="titulo">{music_name}</div>
            <div class="tom">{tom}</div>
                {cifra}
        </div>
    </div>
    """


def _render_footer() -> str:
    return """
    </body>
    </html>
    """


def render_html_document(songs: list[cifra_type.CifraType]) -> str:
    """
    songs = [
        (music_name, tom, cifra),
        (music_name, tom, cifra),
        ...
    ]
    """
    html = _render_header()

    for song in songs:
        html += _render_song_section(song["music_name"], song["tom"], song["cifra"])

    html += _render_footer()
    return html
