from fastapi.testclient import TestClient

from .main import app
import pytest

client = TestClient(app)

user_1 = {"email": "test_user", "password": "123"}


@pytest.fixture(scope="function", autouse=True)
def clean_up():
    client.post("/reset_tables")


def test_add_user():
    response = client.post("/users", json=user_1)
    assert response.status_code == 200

    response = client.get("/users")
    assert response.status_code == 200
    assert any(user["email"] == user_1["email"] for user in response.json()) is True


def test_add_user_multiple_times():
    response = client.post("/users", json=user_1)
    assert response.status_code == 200

    response = client.post("/users", json=user_1)
    assert response.status_code == 400


def test_sign_in():
    response = client.post("/users", json=user_1)
    assert response.status_code == 200

    response = client.post(
        "/token",
        data={
            "username": user_1["email"],
            "password": user_1["password"],
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_sign_in_with_wrong_password():
    response = client.post("/users", json=user_1)
    assert response.status_code == 200

    response = client.post(
        "/token",
        data={
            "username": user_1["email"],
            "password": user_1["password"] + "s",
        },
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
