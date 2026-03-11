from pydantic import BaseModel

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class LoginResponse(BaseModel):
    status: str
    message: str
    similarity: float

class User(UserBase):
    id: int

class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True # Antes llamado orm_mode = True