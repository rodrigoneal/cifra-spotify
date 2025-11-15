class CurrentTrackNotFoundException(Exception):
    def __init__(self, is_playing: bool, currently_playing_type: str) -> None:
        self.is_playing = is_playing
        self.currently_playing_type = currently_playing_type


class PlaylistSeachException(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
