from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest

from ...database import Base
from ...main import app
from ...models import Todos, User
from ...routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id": 1, "username": "testuser", "role": "admin"}

client = TestClient(app)

# Fixtures
@pytest.fixture()
def test_todo():
    todo = Todos(
        title="Test Todo", 
        description="This is a test todo", 
        priority=1, 
        complete=False, 
        owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()

@pytest.fixture()
def test_user():
    user = User(
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="1234567890"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()