import pytest
from fastapi.testclient import TestClient

from ..configuration import settings
from ..database import SessionLocal
from . import test_utils

settings.sqlalchemy_database_url = "sqlite:///./sql_app_test.db"

from ..main import app  # noqa: E402

client = TestClient(app)

user_1 = {"email": "test_user", "password": "123"}
user_2 = {"email": "test_user_2", "password": "123"}

event_1 = {
    "name": "Spotkanie Biznesowe z Klientem",
    "description": "Om\u00f3wienie warunk\u00f3w wsp\u00f3\u0142pracy w restauracji",
    "start_time": "2024-12-05T14:00:00",
    "location": "Warszawa",
    "menu": "Wegetariańskie;Mięsne",
    "decision_deadline": "2024-11-28T12:00:00",
}

guest_1 = {
    "name": "Karolina",
    "surname": "Kowalska",
    "email": "karkowal@gmail.com",
    "phone": "+48765456384",
}


@pytest.fixture(scope="function", autouse=True)
def clean_up():
    client.post("/reset_tables")


def test_add_user():
    response = test_utils.create_user(client=client, user=user_1)

    test_utils.create_admin(SessionLocal(), client, user_2)
    user2_token = test_utils.login_user(client=client, user=user_2)

    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {user2_token}",
        },
    )
    assert response.status_code == 200
    assert any(user["email"] == user_1["email"] for user in response.json()) is True


def test_add_user_multiple_times():
    response = test_utils.create_user(client=client, user=user_1)
    response = client.post("/users", json=user_1)
    assert response.status_code == 400


def test_sign_in():
    assert test_utils.create_user(client=client, user=user_1)
    assert test_utils.login_user(client=client, user=user_1)


def test_sign_in_with_wrong_password():
    assert test_utils.create_user(client=client, user=user_1)

    response = client.post(
        "/token",
        data={
            "username": user_1["email"],
            "password": user_1["password"] + "s",
        },
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_user_email():
    response = test_utils.create_user(client=client, user=user_1)

    user_id = response.json()["user_id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200

    assert "email" in response.json()
    assert response.json()["email"] == user_1["email"]
