from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Mantenemos la relación con usuarios para las playlists
playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    voice_embedding = Column(LargeBinary)
    playlists = relationship("Playlist", back_populates="owner")

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    duration = Column(Integer)
    file_path = Column(String, nullable=False)
    # Almacenamos nombres directamente como strings
    artist_name = Column(String, nullable=False)
    album_title = Column(String, nullable=False)

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary="playlist_songs")