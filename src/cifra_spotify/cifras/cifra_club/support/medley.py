def divisor_medley_default(music_name: str, divisor: str = "/") -> list[str]:
    musics = music_name.split(divisor)
    return [music.strip() for music in musics if music.strip()]
