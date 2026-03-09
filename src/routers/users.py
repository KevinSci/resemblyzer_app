from fastapi import APIRouter, Depends
from .. import models, database
from ..schemas.user import UserCreate
from sqlalchemy.orm import Session



router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("")
async def create_users(user: UserCreate, db: Session = Depends(database.get_db)):
    users = models.User(name=user.name, email=user.email)
    db.add(users)
    db.commit()
    db.refresh(users)
    return users


@router.get("")
async def read_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users

