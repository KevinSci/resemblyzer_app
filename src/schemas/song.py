from pydantic import BaseModel

class SongBase(BaseModel):
    title: str
    duration: int
    artist_name: str
    album_title: str

class SongResponse(SongBase):
    id: int
    file_path: str

    class Config:
        from_attributes = True