from src.cifra_spotify.types import cifra as cifra_type


def _render_header() -> str:
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


def _render_song_section(music_name: str, tom: str, cifra: str) -> str:
    return f"""
    <div class="musica">
        <div class="titulo">{music_name}</div>
        <div class="tom">Tom: {tom.replace("tom:", "")}</div>
        {cifra}
        <hr>
    </div>
    """


def _render_footer() -> str:
    return """
    </div>
    </body>
    </html>
    """


def render_html_document(songs: list[cifra_type.CifraType]) -> str:
    html = _render_header()

    for song in songs:
        html += _render_song_section(song["music_name"], song["tom"], song["cifra"])

    html += _render_footer()
    return html
