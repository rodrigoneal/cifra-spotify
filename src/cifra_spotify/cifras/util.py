import re
import unicodedata

from src.cifra_spotify.app.core.logger import logger

ARTIGOS = {"a", "o", "as", "os", "e"}



def slugify_cifraclub(text: str) -> str:
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
