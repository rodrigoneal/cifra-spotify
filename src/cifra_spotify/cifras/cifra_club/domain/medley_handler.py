import re

from src.cifra_spotify.cifras.cifra_club.domain.types import MedleySplitter
from src.cifra_spotify.cifras.cifra_club.support.medley import (
    divisor_medley_default,
)


class MedleyHandler:
    def __init__(self, splitter: MedleySplitter | None = None) -> None:
        self.splitter = splitter or divisor_medley_default

    def split(self, music: str) -> list[str]:
        return self.splitter(music)

    def is_medley(self, music: str) -> bool:
        parts = self.split(music)
        return len(parts) > 1
