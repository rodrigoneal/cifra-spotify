class CurrentTrackNotFoundException(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code


class PlaylistSeachException(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code


class UserNotAuthenticatedException(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code


class FileNotFoundException(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code


class InvalidFileException(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code


class InvalidFileFormatException(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code


class SpotifyAuthException(Exception):
    pass


class AuthRetry(Exception):
    pass
