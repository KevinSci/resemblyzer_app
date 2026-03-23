from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    voice_embedding: Optional[bytes] = None

class LoginResponse(BaseModel):
    status: str
    message: str
    similarity: float

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True # Antes llamado orm_mode = True