from .utils import *
from ...routers.auth import get_db, authenticate_user,  create_access_token,  SECRET_KEY, ALGORITHM, get_current_user
from fastapi import HTTPException
from jose import jwt
from datetime import timedelta, datetime, timezone
import pytest 

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    user = authenticate_user(db, test_user.username, "testpassword")
    assert user is not None
    assert user.username == test_user.username

    unauthenticated_user = authenticate_user(db, "wronguser", "testpassword")
    assert unauthenticated_user is False

    wrong_password_user = authenticate_user(db, test_user.username, "wrongpassword")
    assert wrong_password_user is False

def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username=username, user_id=user_id, role=role, expires_delta=expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id   
    assert decoded_token["role"] == role
    assert "exp" in decoded_token

@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {"sub": test_user.username, "id": test_user.id, "role": test_user.role, "exp": datetime.now(timezone.utc) + timedelta(days=1)}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)
    assert user == {"id": test_user.id, "username": test_user.username, "role": test_user.role}

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    encode = {"role": "user", "exp": datetime.now(timezone.utc) - timedelta(days=1)}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate user credentials"