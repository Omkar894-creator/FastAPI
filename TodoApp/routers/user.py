from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos, User
from ..database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PasswordUpdateRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User does not exist")
    return db.query(User).filter(User.id == user.get("id")).first()

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, password_update_request: PasswordUpdateRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User does not exist")
    
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not bcrypt_context.verify(password_update_request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    user_model.hashed_password = bcrypt_context.hash(password_update_request.new_password)
    db.commit()

@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, phone_number: str, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User does not exist")

    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.commit()