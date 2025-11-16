import httpx

from bs4 import BeautifulSoup
from src.cifra_spotify.types import cifra as cifra_type


def parse_cifra_page(
    response: httpx.Response, tabs: bool = False
) -> cifra_type.CifraType:
    soup = BeautifulSoup(response.text, "html.parser")
    tom_musica = soup.find("span", id="cifra_tom")
    tom_texto = tom_musica.get_text(strip=True) if tom_musica else ""
    music_name = soup.find("h1", class_="t1").get_text(strip=True)

    pre = soup.find("pre")
    if not tabs:
        tablatures = pre.find_all("span", class_="tablatura")
        for t in tablatures:
            t.decompose()
    return {"tom": tom_texto, "cifra": str(pre), "music_name": music_name}
