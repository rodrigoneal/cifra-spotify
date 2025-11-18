from pydantic import BaseModel


class CurrentlyPlaying(BaseModel):
    track_id: str | None = None
    track_name: str | None = None
    artist_name: str | None = None
    progress_ms: int | None = None
    is_playing: bool = False
