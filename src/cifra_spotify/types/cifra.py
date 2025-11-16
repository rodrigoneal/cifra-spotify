from typing import Callable, TypedDict


class CifraType(TypedDict):
    cifra: str
    tom: str
    music_name: str


MedleySplitter = Callable[[str, str], list[str]]
