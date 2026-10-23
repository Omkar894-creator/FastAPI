from .utils import *
from ...routers.admin import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_todos_authenticated(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title": "Test Todo",
        "description": "This is a test todo",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
        "id": test_todo.id
    }]

def test_admin_delete_todo_authenticated(test_todo):
    response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    deleted_todo = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert deleted_todo is None

def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with id 999 not found"}