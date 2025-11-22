from bs4 import BeautifulSoup

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.schemas.cifraclub.cifraclub_schema import (
    CifraTransportSchema,
)
from src.cifra_spotify.cifras.cifra_base import Instruments
from src.cifra_spotify.cifras.cifra_club.util import slugify_cifraclub


class CifraClubApi:
    def build_url(
        self,
        singer: str,
        music: str,
        instrument: Instruments = Instruments.GUITAR,
    ) -> str:
        """Monta a url para pegar a cifra da musica

        Arguments:
            singer -- nome da musica
            music -- nome do cantor

        Keyword Arguments:
            instrument -- Tipo de Instrumento da Cifra (default: {Instruments.GUITAR})

        Returns:
            str -- url montada
        """
        URL_BASE = "https://cifraclub.com.br/"
        singer = slugify_cifraclub(singer)
        music = slugify_cifraclub(music)
        instrument_str = instrument.value.lower()
        logger.debug(f"Building URL: {singer}/{music}/#instrument={instrument_str}")
        return f"{URL_BASE}{singer}/{music}/#instrument={instrument_str}"

    def build_url_search(self, query: str, slug_url: bool = True) -> str:
        """Monta a url para buscar uma cifra

        Arguments:
            query -- termo de busca

        Returns:
            str -- url montada
        """
        URL_BASE = "https://solr.sscdn.co/cc/h2/?q="
        if slug_url:
            query_slug = slugify_cifraclub(query)
            logger.debug(f"Building Search URL: {URL_BASE}{query_slug}")
            return f"{URL_BASE}{query_slug}"
        else:
            logger.debug(f"Building Search URL: {URL_BASE}{query}")
            return f"{URL_BASE}{query}"

    def parse_cifra_page(
        self, cifra_text: str, tabs: bool = False
    ) -> CifraTransportSchema:
        soup = BeautifulSoup(cifra_text, "html.parser")
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
        else:
            cifra = str(pre)
        tablaturas = pre.find_all("span", class_="tablatura")
        tablatura = None
        if tablaturas:
            if not tabs:
                for t in tablaturas:
                    t.decompose()
            else:
                tablatura = str(tablaturas[0])
        return CifraTransportSchema(
            cifra=cifra, tom=tom_texto, music_name=music_name, tablatura=tablatura
        )
