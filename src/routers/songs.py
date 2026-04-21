from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import uuid
from .. import models, database
from ..schemas.song import SongResponse

router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    responses={404: {"description": "Not found"}},
)

UPLOAD_DIR = Path("media/songs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=SongResponse)
async def upload_song(
    title: str = Form(...),
    duration: int = Form(...),
    artist_name: str = Form(...),
    album_title: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    # Validar formato
    allowed_types = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Formato no permitido.")

    # Guardar archivo físico
    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "mp3"
    unique_filename = f"{uuid.uuid4().hex}_{title.replace(' ', '_')}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de disco: {str(e)}")

    # Guardar en DB con los nombres directos
    new_song = models.Song(
        title=title,
        duration=duration,
        artist_name=artist_name,
        album_title=album_title,
        file_path=str(file_path)
    )
    
    try:
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
    except Exception:
        db.rollback()
        if file_path.exists(): file_path.unlink()
        raise HTTPException(status_code=500, detail="Error en base de datos.")

    return new_song

@router.get("/{song_id}/play")
async def play_song(song_id: int, db: Session = Depends(database.get_db)):
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song or not Path(song.file_path).exists():
        raise HTTPException(status_code=404, detail="Archivo no disponible.")
    return FileResponse(path=song.file_path, media_type="audio/mpeg")