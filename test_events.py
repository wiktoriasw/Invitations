import pytest
from fastapi.testclient import TestClient

from . import test_utils
from .configuration import settings
from .main import app

settings.sqlalchemy_database_url = "sqlite:///./sql_app_test.db"


client = TestClient(app)

user_1 = {"email": "test_user", "password": "123"}

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


def test_create_event():
    assert test_utils.create_user(client=client, user_1=user_1)
    token = test_utils.login_user(client=client, user_1=user_1)

    response = client.post(
        "/events",
        json=event_1,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200

    assert response.json()["name"] == event_1["name"]
    assert response.json()["description"] == event_1["description"]


def test_delete_event():
    assert test_utils.create_user(client=client, user_1=user_1)
    token = test_utils.login_user(client=client, user_1=user_1)

    response = client.post(
        "/events",
        json=event_1,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200

    event_uuid = response.json()["uuid"]
    assert event_uuid is not None

    response = client.delete(
        f"events/{event_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/events/{event_uuid}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404
