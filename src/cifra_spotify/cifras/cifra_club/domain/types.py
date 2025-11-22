from typing import Callable, TypeAlias, TypedDict


class CifraType(TypedDict):
    cifra: str
    tom: str
    music_name: str


MedleySplitter: TypeAlias = Callable[[str, str], list[str]]
