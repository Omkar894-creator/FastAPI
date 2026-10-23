from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field 
from ..models import User 
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import SessionLocal 
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.templating import Jinja2Templates

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=10)

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "oouwehff089348yuiuguhh3798th988"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")

###Pages###

@router.get("/login-page")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@router.get("/register-page")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

from jose import JWTError, jwt
from fastapi import HTTPException, status

# def get_current_user(token: str | None):
#     if not token:
#         return None

#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )

#         username: str = payload.get("sub")
#         user_id: str = payload.get("id")
#         user_role: str = payload.get("role")

#         if username is None or user_id is None:
#             return None

#         return {
#             "username": username,
#             "id": user_id,
#             "role": user_role
#         }

#     except JWTError:
#         return None
    
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user credentials")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user credentials") from e

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: CreateUserRequest, db: db_dependency):
    create_user_model = User(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
        is_active=True,
        phone_number=user_request.phone_number,
        )

    db.add(create_user_model)
    db.commit()

    return create_user_model

@router.post("/token")
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return {"error": "Invalid username or password"}
    access_token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return Token(access_token=access_token, token_type="bearer")