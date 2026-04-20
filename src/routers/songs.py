from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
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

# Directorio local para guardar las canciones (asegura que exista)
UPLOAD_DIR = Path("media/songs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=SongResponse)
async def upload_song(
    title: str = Form(...),
    duration: int = Form(..., description="Duración en segundos"),
    album_id: int = Form(...),
    artist_id: int = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    # 1. Validar que el artista y el álbum existan para evitar errores de llave foránea
    artist = db.query(models.Artist).filter(models.Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="El artista especificado no existe.")
        
    album = db.query(models.Album).filter(models.Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="El álbum especificado no existe.")

    # 2. Validar formato del archivo
    allowed_types = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/ogg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Formato de audio inválido. Solo se permite mp3, wav o ogg.")

    # 3. Generar un nombre único para evitar sobreescribir archivos con el mismo nombre
    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "mp3"
    unique_filename = f"{uuid.uuid4().hex}_{title.replace(' ', '_')}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # 4. Guardar el archivo en el disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")

    # 5. Persistir metadatos en la base de datos
    new_song = models.Song(
        title=title,
        duration=duration,
        album_id=album_id,
        artist_id=artist_id,
        file_path=str(file_path) # Guardamos la ruta estática
    )
    
    try:
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
    except Exception as e:
        db.rollback()
        # Si falla la base de datos, eliminamos el archivo huérfano por limpieza
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail="Error al guardar en la base de datos.")

    return new_song

@router.get("/", response_model=list[SongResponse])
async def get_songs(db: Session = Depends(database.get_db)):
    """Obtiene la lista de todas las canciones subidas."""
    return db.query(models.Song).all()