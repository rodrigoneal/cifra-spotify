import re
import unicodedata
from urllib.parse import urlparse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cifra_spotify.cifras.parsers.spotify import SongData

from rapidfuzz import fuzz

from cifra_spotify.cifras.search.ranking import normalize_text
from src.cifra_spotify.app.core.logger import logger

ARTIGOS = {"a", "o", "as", "os", "e"}

STOPWORDS_ARTISTA = {
    "grupo",
    "banda",
    "band",
    "orquestra",
}


def normalize_track_title(title: str) -> str:
    """
    Normaliza o título de uma música removendo informações extras comuns
    em metadados de plataformas de streaming, como versões ao vivo,
    acústicas ou remasterizadas.

    A função remove termos entre parênteses, colchetes ou hífens que
    contenham palavras relacionadas a versões da música.

    Exemplos removidos:
    - (Ao Vivo)
    - (Live)
    - (Live at ...)
    - (Acoustic)
    - (Remastered 2011)
    - - Ao Vivo
    - - Live Version
    - [Live]

    Parâmetros
    ----------
    title : str
        Título original da música retornado pela API do Spotify
        ou outra fonte de metadados.

    Retorno
    -------
    str
        Título da música normalizado, contendo apenas o nome principal.

    Exemplos
    --------
    >>> normalize_track_title("Evidências (Ao Vivo)")
    'Evidências'

    >>> normalize_track_title("Hotel California - Live")
    'Hotel California'

    >>> normalize_track_title("Tempo Perdido (Remastered 2015)")
    'Tempo Perdido'
    """

    if not title:
        return title

    # Palavras que indicam versões da música
    keywords = [
        "live",
        "ao vivo",
        "acoustic",
        "remaster",
        "remastered",
        "version",
        "edit",
        "mix",
        "deluxe",
    ]

    # Remove conteúdos entre () ou []
    pattern_parentheses = r"[\(\[].*?[\)\]]"
    parts = re.findall(pattern_parentheses, title)

    for part in parts:
        if any(k in part.lower() for k in keywords):
            title = title.replace(part, "")

    # Remove sufixos após hífen
    parts = re.split(r"\s-\s", title)
    if len(parts) > 1:
        if any(k in parts[-1].lower() for k in keywords):
            title = parts[0]

    # Limpeza final
    title = re.sub(r"\s{2,}", " ", title).strip()

    return title


def slugify_cifraclub(text: str) -> str:
    """
    Converts a text string into a slug compatible with CifraClub URLs.

    This function normalizes the text by removing accents, converting to
    lowercase, removing special characters, and replacing spaces with hyphens.
    It also removes Portuguese articles (defined in ARTIGOS) from the text,
    except for the first word, to better match the slug format used by
    CifraClub URLs.

    Example:
        "O Amor de Deus" -> "o-amor-deus"

    Args:
        text (str): Input text, usually a music title or artist name.

    Returns:
        str: Slugified version of the text suitable for URL usage.
    """
    logger.debug(f"Slugifying: {text}")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # minusculo e apenas letras/numeros/espaco
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)

    palavras = text.split()

    if not palavras:
        return ""

    # mantém a primeira palavra sempre
    primeira = palavras[0]

    # remove artigos apenas a partir da segunda palavra
    resto = [p for p in palavras[1:] if p not in ARTIGOS]

    palavras_final = [primeira] + resto

    return "-".join(palavras_final)


def normalize_artist_name(text: str) -> str:
    text = normalize_text(text)
    words = [w for w in text.split() if w not in STOPWORDS_ARTISTA]
    return " ".join(words)


def compare_artist_name(text1: str, text2: str, threshold: int = 80) -> bool:
    t1 = normalize_artist_name(text2).lower()
    t2 = normalize_artist_name(text1).lower()

    score = fuzz.token_sort_ratio(t1, t2)

    return {
        "text1": text1,
        "text2": text2,
        "normalized1": t1,
        "normalized2": t2,
        "score": score,
        "match": score >= threshold,
    }


def compare_track(text1: str, text2: str, threshold: int = 80):
    t1 = normalize_track_title(text1).lower()
    t2 = normalize_track_title(text2).lower()

    score = fuzz.token_sort_ratio(t1, t2)

    return {
        "text1": text1,
        "text2": text2,
        "normalized1": t1,
        "normalized2": t2,
        "score": score,
        "match": score >= threshold,
    }


def html_to_text(html: str) -> str:
    text = re.sub(r"</?(pre|b)>", "", html)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def extract_artist_from_url(url: str) -> str | None:
    path = urlparse(url).path.strip("/").split("/")
    if not path:
        return None

    slug = path[0]
    slug = slug.replace("-musicas", "")
    return " ".join(part.capitalize() for part in slug.split("-"))


def improve_response(items: list[dict], song_data: type["SongData"]) -> dict:
    results = []

    for item in items:
        html = item.get("cifra", "")
        text = html_to_text(html)

        results.append(
            {
                "title": item.get("music_name"),
                "artist": extract_artist_from_url(item.get("url", "")),
                "artist_spotify_id": song_data.artist_id,
                "genres": song_data.genres,
                "key": item.get("tom"),
                "instrument": "guitar",
                "source": "Cifra Club",
                "url": item.get("url"),
                "preview": " ".join(text.splitlines()[2:5])[:160],
                "metadata": {
                    "has_html_formatting": "<b>" in html or "<pre>" in html,
                    "has_lyrics": True,
                    "has_chords": True,
                },
            }
        )

    return {
        "success": True,
        "count": len(results),
        "results": results,
    }
