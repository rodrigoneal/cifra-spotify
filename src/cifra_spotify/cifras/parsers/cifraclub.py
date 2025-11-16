import httpx
from bs4 import BeautifulSoup

from src.cifra_spotify.types import cifra as cifra_type


def parse_cifra_page(
    response: httpx.Response, tabs: bool = False
) -> cifra_type.CifraType:
    soup = BeautifulSoup(response.text, "html.parser")
    tom_musica = soup.find("span", id="cifra_tom")
    tom_texto = tom_musica.get_text(strip=True) if tom_musica else ""
    element = soup.find("h1", class_="t1")
    if element:
        music_name = element.get_text(strip=True)
    else:
        raise ValueError("Music name not found")

    pre = soup.find("pre")
    if not pre:
        raise ValueError("Cifra not found")
    if not tabs:
        tablatures = pre.find_all("span", class_="tablatura")
        for t in tablatures:
            t.decompose()
    return {"tom": tom_texto, "cifra": str(pre), "music_name": music_name}
