from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from .. import models, database
from ..schemas.user import UserCreate, UserBase, UserResponse, LoginResponse
from sqlalchemy.orm import Session
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import tempfile
import shutil
from pathlib import Path

encoder = VoiceEncoder()

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=UserResponse)
async def create_users(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    if audio.content_type not in ["audio/mpeg", "audio/wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Formato de audio invalido")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(audio.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        wav_audio = preprocess_wav(tmp_path)
        embed = encoder.embed_utterance(wav_audio)
        user = models.User(name=name, email=email, password=password, voice_embedding=embed.tobytes())
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path.exists(): tmp_path.unlink()

    return user


@router.post("/login", response_model=LoginResponse)
async def login_user(
    email: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(audio.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        wav_audio = preprocess_wav(tmp_path)
        login_embed = encoder.embed_utterance(wav_audio)
    finally:
        if tmp_path.exists(): tmp_path.unlink()

    master_embed = np.frombuffer(user.voice_embedding, dtype=np.float32)
    similarity = np.inner(master_embed, login_embed)

    UMBRAL = 0.80
    if similarity < UMBRAL:
        raise HTTPException(status_code=401, detail=f"Acceso denegado. Similitud: {similarity:.2f}")
    
    return LoginResponse(
        status="Success",
        message=f"Acceso permitido, hola {user.name}",
        similarity=float(similarity)
    )

@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users