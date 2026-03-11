from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from .. import models, database
from ..schemas.user import UserCreate, UserBase, UserResponse
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

@router.post("/register")
async def create_users(
    name: str = Form(...),
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

        user = models.User(name=name, voice_emmbedding=embed.tobytes())
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        if tmp_path.exists(): tmp_path.unlink()

    return {"message": "User created successfully", "user_id": user.id, "name": user.name, "audio": audio.filename, "audio_type": audio.content_type, "embed": embed.tolist()}


@router.post("/login")
async def login_user(
    name: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    user = db.query(models.User).filter(models.User.name == name).first()
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

    master_embed = np.frombuffer(user.voice_emmbedding, dtype=np.float32)
    similarity = np.inner(master_embed, login_embed)

    UMBRAL = 0.80
    if similarity < UMBRAL:
        raise HTTPException(status_code=401, detail=f"Acceso denegado. Similitud: {similarity:.4f}")
    
    return {
        "status": "success",
        "message": f"Bienvenido {user.name}",
        "similarity": float(similarity)
    
    }

@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users