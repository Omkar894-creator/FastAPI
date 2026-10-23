from .utils import *
from ...routers.user import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 1
    assert response.json()['username'] == "testuser"
    assert response.json()['email'] == "testuser@example.com"
    assert response.json()['first_name'] == "Test"
    assert response.json()['last_name'] == "User"
    assert response.json()['role'] == "admin"
    assert response.json()['phone_number'] == "1234567890"

def test_update_password(test_user):
    response = client.put("/user/password", json={
        "old_password": "testpassword",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_update_wrong_old_password(test_user):
    response = client.put("/user/password", json={
        "old_password": "wrongpassword",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Old password is incorrect"}

def test_update_phone_number(test_user):
    new_phone_number = "0987654321"
    response = client.put(f"/user/phone_number/{new_phone_number}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify that the phone number was updated
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['phone_number'] == new_phone_number