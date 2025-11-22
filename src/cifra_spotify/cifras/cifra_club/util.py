import re
import unicodedata

from src.cifra_spotify.app.core.logger import logger

ARTIGOS = {"a", "o", "as", "os", "e"}


def slugify_cifraclub(text: str) -> str:
    logger.debug(f"Slugifying: {text}")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)

    palavras = text.split()

    if not palavras:
        return ""

    # mantém a primeira palavra sempre
    primeira = palavras[0]

    # remove artigos apenas a partir da segunda palavra
    resto = [p for p in palavras[1:] if p not in ARTIGOS]

    palavras_final = [primeira] + resto

    return "-".join(palavras_final)


def clean_artist_name(name: str) -> str:
    """Limpar o nome do artista na busca do cifraclub

    Arguments:
        name -- nome do cantor/grupo/conjunto/etc...

    Returns:
        nome normalizado para busca
    """
    name = name.lower()

    # remove coisas entre parênteses ou colchetes
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)

    # remove participações
    name = re.sub(
        r"\b(feat|ft|participa(?:cao|ção)|part\.?|featuring)\b.*",
        "",
        name,
    )

    # remove termos que sujam o nome, incluindo "grupo"
    name = re.sub(
        r"\b(grupo|banda|ao vivo|versao|versão|oficial|video|vídeo|acústico|acustico)\b",
        "",
        name,
    )

    # remove caracteres indesejados (mas mantém espaço e -)
    name = re.sub(r"[^a-z0-9\s\-]", "", name)

    # normaliza múltiplos espaços
    name = re.sub(r"\s{2,}", " ", name)

    return name.strip()
