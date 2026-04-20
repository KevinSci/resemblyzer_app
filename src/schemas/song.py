from pydantic import BaseModel
from typing import Optional

class SongBase(BaseModel):
    title: str
    duration: int
    album_id: int
    artist_id: int

class SongResponse(SongBase):
    id: int
    file_path: str

    class Config:
        from_attributes = True