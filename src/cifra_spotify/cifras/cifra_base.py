from abc import ABC
from enum import Enum


class Instruments(str, Enum):
    GUITAR = "guitar"
    KEYBOARD = "keyboard"
    CAVACO = "cavaco"
    UKULELE = "ukulele"


class Cifra(ABC):
    async def get_cifra(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ) -> str:
        raise NotImplementedError

    async def search_cifra_in_ddg(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ) -> str:
        raise NotImplementedError
