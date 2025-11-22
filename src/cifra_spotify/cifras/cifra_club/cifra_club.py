import asyncio

from rapidfuzz import fuzz

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.schemas.cifraclub.cifraclub_schema import (
    CifraTransportSchema,
)
from src.cifra_spotify.cifras.cifra import Cifra
from src.cifra_spotify.cifras.cifra_base import CifraBase, Instruments
from src.cifra_spotify.cifras.cifra_club.domain.api import CifraClubApi
from src.cifra_spotify.cifras.cifra_club.domain.medley_handler import MedleyHandler
from src.cifra_spotify.cifras.cifra_club.infrastructure.http.http_client import (
    CifraClubHttpClient,
)
from src.cifra_spotify.cifras.cifra_club.util import clean_artist_name


class CifraClub(CifraBase):
    url_base = "https://cifraclub.com.br/"

    def __init__(
        self,
        client: CifraClubHttpClient,
    ) -> None:
        self.client = client
        self.cifra_client = client
        self.api = CifraClubApi()

    def _verify_music(self, musics_response: str, singer_name: str) -> bool:
        if musics_response and musics_response["response"]["numFound"] > 0:
            _singer = musics_response["response"]["docs"][0]["d"]
            music = musics_response["response"]["docs"][0]["u"]
            if fuzz.partial_ratio(_singer, singer_name) > 80:
                return music
        return False

    async def search(self, query: str, slug_url: bool = True) -> dict | None:
        """Busca cifras no cifra club

        Arguments:
            query -- termo de busca

        Returns:
            list[CifraTransportSchema] -- Lista de cifras encontradas
        """
        logger.info(f"Searching cifra: {query}")
        response = await self.cifra_client.fetch_page(
            self.api.build_url_search(query, slug_url=slug_url)
        )
        if response.status_code == 200:
            return eval(response.text)
        return None

    async def filter_music(self, singer_name: str, music: str) -> list[str]:
        medley_handler = MedleyHandler()

        async def find_music(query: str) -> str | None:
            response = await self.search(query)
            return self._verify_music(response, singer_name)

        full_match = await find_music(music)
        if full_match:
            return [full_match]

        if not medley_handler.is_medley(music):
            return [music]

        musics = []
        for part in medley_handler.split(music):
            validated = await find_music(part)
            if validated:
                musics.append(validated)

        return musics or [music]

    def match_singer_name(self, singers: list, original_name: str) -> str:
        """
        Retorna o nome correto do cantor a partir da lista de docs do search.
        Mantém exatamente a lógica atual do usuário.
        """
        _clean = clean_artist_name(original_name)

        for singer in singers:
            candidate = singer["d"]

            if (
                fuzz.partial_ratio(candidate, _clean) > 80
                or fuzz.partial_ratio(candidate, f"grupo {_clean}") > 80
            ):
                return candidate  # Encontrado

        return original_name  # Não encontrado

    async def resolve_singer_name(self, singer: str) -> str:
        """
        Limpa o nome do cantor, busca no índice e tenta encontrar o melhor match.
        Se não encontrar nada relevante, retorna o nome original.
        """
        cleaned = clean_artist_name(singer)
        search_response = await self.search(cleaned)

        if not search_response:
            return singer

        docs = search_response["response"].get("docs", [])
        if not docs:
            return singer

        return self.match_singer_name(docs, singer)

    async def resolve_singer_and_music(
        self, singer: str, music: str
    ) -> tuple[str, str]:
        """
        Faz uma última tentativa de resolver o cantor + música combinados.
        Se encontrar algo, retorna (novo_singer, nova_music).
        Caso contrário, retorna (singer, music) originais.
        """
        query = f"{singer} {music}"
        response = await self.search(query, slug_url=False)

        if not response:
            return singer, music

        docs = response.get("response", {}).get("docs", [])
        if not docs:
            return singer, music

        # Pegamos o primeiro doc, já que Solr normalmente ordena por score
        doc = docs[0]

        # m = music name
        # a = artist name
        new_music = doc.get("m", music) or music
        new_singer = doc.get("a", singer) or singer

        return new_singer, new_music

    async def prepare(
        self,
        singer: str,
        music: str,
        tabs: bool,
        instrument: Instruments = Instruments.GUITAR,
    ) -> dict[str, list[str] | str]:
        """Prepara para a requisição da cifra.

        Arguments:
            singer -- Nome da musica.
            music -- Nome do cantor
            tabs -- Se deseja a tablatura na cifra

        Keyword Arguments:
            instrument -- Tipo de Instrumento da cifra (default: {Instruments.GUITAR})

        Returns:
            CifraTransportSchema -- Schema com os dados da cifra[cifra, tom, musica_name]
        """

        singer_name = await self.resolve_singer_name(singer)
        musics = await self.filter_music(singer_name, music)
        singer_name, music = await self.resolve_singer_and_music(singer_name, music)
        return {"musics": musics, "singer_name": singer_name}

    async def _fetch_single_cifra(
        self,
        singer: str,
        music: str,
        tabs: bool,
        instrument: Instruments,
    ) -> CifraTransportSchema:
        response = await self.cifra_client.fetch_page(
            self.api.build_url(singer, music, instrument)
        )
        if response.status_code != 200 or len(response.url.path) < 2:
            raise ValueError(f"Error fetching cifra: {response.status_code}")
        return self.api.parse_cifra_page(response.text, tabs)

    async def fetch(
        self,
        singer: str,
        music: str,
        tabs: bool,
        instrument: Instruments = Instruments.GUITAR,
    ) -> Cifra:
        """Prepara para a requisição da cifra.

        Arguments:
            singer -- Nome da musica.
            music -- Nome do cantor
            tabs -- Se deseja a tablatura na cifra

        Keyword Arguments:
            instrument -- Tipo de Instrumento da cifra (default: {Instruments.GUITAR})

        Returns:
            CifraTransportSchema -- Schema com os dados da cifra[cifra, tom, musica_name]
        """
        result_prepared = await self.prepare(singer, music, tabs, instrument)
        singer = result_prepared["singer_name"]
        musics = result_prepared["musics"]
        if not musics:
            raise ValueError("Musics not found")

        tasks = [
            asyncio.create_task(
                self._fetch_single_cifra(singer, music, tabs, instrument)
            )
            for music in musics
        ]
        cifras = []
        for task in asyncio.as_completed(tasks):
            cifra = await task
            cifras.append(cifra)
        return Cifra(cifras)
