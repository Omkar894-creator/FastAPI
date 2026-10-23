from fastapi import status

from ..todos import get_db
from ..auth import get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Test cases
def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title": "Test Todo",
        "description": "This is a test todo",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
        "id": test_todo.id
    }]

def test_read_todo_authenticated(test_todo):
    response = client.get(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Test Todo",
        "description": "This is a test todo",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
        "id": test_todo.id
    }

def test_read_todo_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}

def test_create_todo_authenticated(test_todo):
    todo_data = {
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 2,
        "complete": False
    }
    response = client.post("/todos/todo", json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    created_todo = db.query(Todos).filter(Todos.id == 2).first()
    assert created_todo.title == todo_data["title"]
    assert created_todo.description == todo_data["description"]
    assert created_todo.priority == todo_data["priority"]
    assert created_todo.complete == todo_data["complete"]

def test_update_todo_authenticated(test_todo):
    update_data = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 3,
        "complete": True
    }
    response = client.put(f"/todos/todo/{test_todo.id}", json=update_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    updated_todo = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert updated_todo.title == update_data["title"]
    assert updated_todo.description == update_data["description"]
    assert updated_todo.priority == update_data["priority"]
    assert updated_todo.complete == update_data["complete"]

def test_update_todo_not_found():
    update_data = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 3,
        "complete": True
    }
    response = client.put("/todos/todo/999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}

def test_delete_todo_authenticated(test_todo):
    response = client.delete(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    deleted_todo = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert deleted_todo is None

def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}