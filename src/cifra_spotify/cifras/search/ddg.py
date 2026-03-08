from ddgs import DDGS

from cifra_spotify.cifras.enum import SitesCifra


def montar_query_cifra(
    site_name: SitesCifra, song_name: str, artist_name: str | None = None
) -> str:
    base = f'site:{site_name.value} "{song_name}"'
    if artist_name:
        base += f" {artist_name}"
    return base + " cifra"


def buscar_cifra_duckduckgo(
    site_name: SitesCifra,
    song_name: str,
    artist_name: str | None = None,
    max_results: int = 10,
) -> dict:
    """
    Faz uma busca no DuckDuckGo e retorna os resultados em formato JSON serializável.

    Observação:
    - Isso faz scraping da página HTML de resultados.
    - Não depende de endpoint JSON oficial de busca web tradicional.
    - Para cifras, vale usar operadores como:
      site:cifraclub.com.br "nome da musica" artista cifra

    Parâmetros
    ----------
    query : str
        Texto da busca.

    Retorno
    -------
    dict
        Estrutura com query, url e lista de resultados.
    """

    ddg = DDGS()
    query = montar_query_cifra(site_name, song_name, artist_name)
    breakpoint()
    results = ddg.text(query, max_results=max_results)
    return results
