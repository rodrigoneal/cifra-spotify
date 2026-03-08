import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalizes a text string for comparison.

    The normalization removes accents, converts the text to lowercase,
    and trims surrounding whitespace. This helps ensure consistent
    string comparisons regardless of accents or case differences.

    Example:
        "Díana " -> "diana"

    Args:
        text (str): Input text to normalize.

    Returns:
        str: Normalized text.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


def contains_word(text: str, term: str) -> bool:
    """
    Checks whether a specific word exists in a text.

    Both the text and the term are normalized (lowercase, no accents)
    before the search. The function uses word boundaries to avoid
    partial matches.

    Example:
        contains_word("Diana - Porque Brigamos", "diana") -> True

    Args:
        text (str): Text where the search will be performed.
        term (str): Word to search for.

    Returns:
        bool: True if the term appears as a whole word in the text,
        otherwise False.
    """
    text = normalize_text(text)
    term = normalize_text(term)
    pattern = rf"\b{re.escape(term)}\b"
    return bool(re.search(pattern, text))


def score_result(result: dict, music_name: str, artist: str) -> int:
    """
    Calculates a relevance score for a search result.

    The score is based on how well the result matches the requested
    music title and artist. Matches in the title, URL, and body are
    weighted differently.

    Scoring priorities:
        - Artist match in title (highest weight)
        - Artist match in URL
        - Artist match in body
        - Music name match in title, URL, or body
        - Penalization for results that contain only lyrics
          (e.g. "/letra/") or non-cifra pages.

    Higher scores indicate more relevant results.

    Args:
        result (dict): Search result containing fields such as
            "title", "href", and "body".
        music_name (str): Name of the music being searched.
        artist (str): Artist name being searched.

    Returns:
        int: Relevance score used to rank search results.
    """
    title = result.get("title", "")
    href = result.get("href", "")
    body = result.get("body", "")

    title_n = normalize_text(title)
    href_n = normalize_text(href)
    body_n = normalize_text(body)
    # artist_n = normalize_text(artist)
    music_n = normalize_text(music_name)

    score = 0

    # Prioridade máxima: artista correto
    if contains_word(title, artist):
        score += 100
    if contains_word(href.replace("-", " ").replace("/", " "), artist):
        score += 80
    if contains_word(body, artist):
        score += 30

    # Música correta
    if music_n and music_n in title_n:
        score += 40
    if music_n and music_n in href_n:
        score += 20
    if music_n and music_n in body_n:
        score += 10

    # Priorizar cifra e penalizar letra apenas
    if (
        "/letra/" in href_n
        or "(letra da musica)" in title_n
        or "/discografia/" in title_n
    ):
        score -= 50
    else:
        score += 15

    return score


def sort_results_by_relevance(
    results: list[dict], music_name: str, artist: str
) -> list[dict]:
    """
    Sorts search results by relevance based on the music title and artist.

    Each result is scored using the `score_result` function, and the
    results are ordered from most relevant to least relevant.

    Args:
        results (list[dict]): List of search results returned by the
            search engine.
        music_name (str): Name of the music being searched.
        artist (str): Artist name being searched.

    Returns:
        list[dict]: Results sorted by descending relevance.
    """
    return sorted(
        results,
        key=lambda item: score_result(item, music_name, artist),
        reverse=True,
    )


def should_exclude_lyrics_only(result: dict) -> bool:
    """
    Determines whether a search result should be excluded because it does not
    represent a chord sheet (cifra) page.

    This function filters out results that correspond to:
        - Lyrics-only pages
        - Discography pages listing all songs from an artist

    The following patterns are considered non-cifra pages:
        - URLs containing "/letra/" (lyrics-only pages)
        - Titles containing "(letra da musica)"
        - URLs containing "/discografia/" (artist discography pages)

    Args:
        result (dict): Search result dictionary expected to contain the keys
            "title" and "href".

    Returns:
        bool: True if the result should be excluded (not a chord sheet page),
        False otherwise.
    """
    title = result.get("title", "")
    href = result.get("href", "")

    title_n = normalize_text(title)
    href_n = normalize_text(href)

    return (
        "/letra/" in href_n
        or "(letra da musica)" in title_n
        or "/discografia/" in href_n
    )
