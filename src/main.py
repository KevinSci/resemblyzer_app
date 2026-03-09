from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from .routers import users
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (controladores)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}



from resemblyzer import VoiceEncoder, preprocess_wav

@app.post("/audio")
async def proccess_audio(audio: UploadFile = File(...)):
    if audio.content_type not in ["audio/mpeg", "audio/wav", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    wav_audio = preprocess_wav(audio.file)
    encoder = VoiceEncoder()
    embed = encoder.embed_utterance(wav_audio)
    return embed

